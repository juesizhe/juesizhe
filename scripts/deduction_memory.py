#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觉思者 · 推演记忆防膨胀工具（零依赖 · 仅标准库 · Windows 可用）

解决的问题
----------
1. 推演历史（PHILOSOPHY.md）无限堆叠 → 上下文 token 爆炸。
2. 计数器只存在于内存 → 定时任务重启后清零，永远触发不了摘要压缩。
3. “token 数”由模型自估 → 不可复现。这里给出确定性估算，闸门才可靠。

设计原则
--------
- 原始档案 PHILOSOPHY.md **只追加、永不删**，本脚本不含任何删除/清空它的能力。
- 计数器的写盘走「文件锁 + 临时文件 + os.replace 原子替换」，8 场定时推演并发也不会丢计数。
- 所有阈值集中在 THRESHOLDS，一处改全局生效。

命令
----
  status                    总览：轮次 / 是否该压缩 / 摘要与档案体量
  get                       读取当前轮次
  incr [--note "..."]       完成一轮推演后 +1 并回写（持久化）
  reset                     压缩成功后把轮次归零
  should-compress           该压缩则 exit 0，否则 exit 1（供脚本分支判断）
  summary-check             摘要是否逼近上限、需二次浓缩 → 需则 exit 0
  tokens <file> [--mode mid|high|low]   确定性 token 估算
  archive-stats             档案体量，并给出 full / incremental 建议
  prepare-compress          输出本次压缩的执行计划（JSON）
  mark-compressed           压缩成功后：更新水位线、压缩时间、累计次数、轮次归零
  compress-fail --reason .. 压缩失败：记录日志，轮次**不**归零（下轮重试）
  fragment --pattern P [--context N] [--max-chars M]   有界局部检索（绝不返回全量）
  log --event "..."         追加一行压缩/异常事件日志
  selftest                  内建测试（RED-GREEN 用的 GREEN 校验）

用法示例：
  python scripts/deduction_memory.py status
  python scripts/deduction_memory.py incr --note "T012 白天推演"
  python scripts/deduction_memory.py prepare-compress
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

# --------------------------------------------------------------------------
# 配置
# --------------------------------------------------------------------------

SKILL_ROOT = Path(__file__).resolve().parent.parent

THRESHOLDS = {
    # 每完成几次「完整推演循环」触发一次摘要压缩
    "compress_every": 5,
    # 摘要硬上限（token，mid 估算值）。超过即违规，须再压。
    "summary_token_cap": 4000,
    # 摘要达到此值即触发「二次再浓缩」（预留余量，避免贴着上限走）
    "summary_recondense_at": 3400,
    # 字符数硬兜底：token 估算有误差，字符数是确定性指标（≈4400 中文字符）
    "summary_char_cap": 5200,
    # 档案超过此字节数，压缩由「全量重压」自动降级为「增量压缩」
    "archive_incremental_bytes": 200 * 1024,
    # 局部检索单次返回上限（字符），保证「只读取局部片段」
    "fragment_max_chars": 8000,
}

FILES = {
    "counter": "run_counter.md",
    "archive": "PHILOSOPHY.md",
    "summary": "PHILOSOPHY_SUMMARY.md",
    "log": "PHILOSOPHY_SUMMARY.log.md",
}

COUNTER_KEYS = [
    "推演累计轮次",
    "压缩阈值",
    "上次推演时间",
    "上次压缩时间",
    "累计压缩次数",
    "已压缩至行数",
    "状态",
    "备注",
]

CJK_RE = re.compile(
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3040-\u30ff\uac00-\ud7af]"
)
WORD_RE = re.compile(r"[A-Za-z0-9_']+")


# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------

def now_str() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def atomic_write(path: Path, text: str) -> None:
    """临时文件 + os.replace：要么整份生效，要么完全不生效。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


_HELD_LOCKS: dict = {}


class FileLock:
    """极简互斥锁：O_EXCL 创建，陈旧锁超时自动回收。

    同一进程内**可重入**（incr 外层持锁 → write_counter 内层再次请求同一文件时不会自锁）。
    """

    def __init__(self, path: Path, timeout: float = 10.0, stale: float = 60.0):
        self.path = Path(str(path) + ".lock")
        self.timeout = timeout
        self.stale = stale
        self.held = False

    def __enter__(self):
        key = str(self.path)
        if key in _HELD_LOCKS:
            _HELD_LOCKS[key] += 1
            return self
        deadline = time.time() + self.timeout
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                _HELD_LOCKS[key] = 1
                self.held = True
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.path) > self.stale:
                        os.unlink(self.path)
                        continue
                except FileNotFoundError:
                    continue
                if time.time() > deadline:
                    raise TimeoutError(f"无法获得锁：{self.path}")
                time.sleep(0.05)

    def __exit__(self, *exc):
        key = str(self.path)
        if key in _HELD_LOCKS:
            _HELD_LOCKS[key] -= 1
            if _HELD_LOCKS[key] > 0:
                return False
            del _HELD_LOCKS[key]
        if self.held:
            try:
                os.unlink(self.path)
            except FileNotFoundError:
                pass
        return False


def est_tokens(text: str, mode: str = "mid") -> int:
    """确定性 token 估算（不依赖任何分词器）。

    mid（默认，用于闸门）: CJK 0.9 / 拉丁词 1.3 / 其他非空白字符 0.5
    high（保守上界）      : CJK 1.4 / 拉丁词 1.4 / 其他 1.0
    low （乐观下界）      : CJK 0.6 / 拉丁词 1.0 / 其他 0.3
    """
    if not text:
        return 0
    cjk = len(CJK_RE.findall(text))
    words = len(WORD_RE.findall(text))
    rest = WORD_RE.sub(" ", CJK_RE.sub(" ", text))
    other = sum(1 for ch in rest if not ch.isspace())
    if mode == "high":
        return int(cjk * 1.4 + words * 1.4 + other * 1.0)
    if mode == "low":
        return int(cjk * 0.6 + words * 1.0 + other * 0.3)
    return int(cjk * 0.9 + words * 1.3 + other * 0.5)


def read_text(path: Path) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def count_lines(path: Path) -> int:
    p = Path(path)
    if not p.exists():
        return 0
    with p.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


# --------------------------------------------------------------------------
# 计数器（run_counter.md）
# --------------------------------------------------------------------------

def counter_path() -> Path:
    return SKILL_ROOT / FILES["counter"]


def read_counter() -> dict:
    raw = read_text(counter_path())
    out = {}
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">"):
            continue
        m = re.match(r"^([^\s:：]+)\s*[:：]\s*(.*?)\s*$", s)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def get_rounds() -> int:
    v = read_counter().get("推演累计轮次", "0")
    m = re.search(r"\d+", v)
    return int(m.group()) if m else 0


def write_counter(updates: dict) -> None:
    p = counter_path()
    with FileLock(p):
        raw = read_text(p)
        lines = raw.splitlines() if raw else []
        seen = set()
        out = []
        for ln in lines:
            m = re.match(r"^\s*([^\s:：]+)\s*[:：]", ln)
            if m and m.group(1) in updates:
                k = m.group(1)
                out.append(f"{k}: {updates[k]}")
                seen.add(k)
            else:
                out.append(ln)
        for k, v in updates.items():
            if k not in seen:
                out.append(f"{k}: {v}")
        atomic_write(p, "\n".join(out).rstrip() + "\n")


def ensure_counter() -> None:
    p = counter_path()
    if p.exists():
        return
    text = (
        "# 觉思者 · 推演轮次计数器（持久化 · 重启不清零）\n"
        "\n"
        "> 由 `scripts/deduction_memory.py` 独占维护。**勿手工改数字**——\n"
        "> 定时任务重启后靠它恢复计数，清零会导致永远触发不了摘要压缩。\n"
        "> `已压缩至行数` 是 PHILOSOPHY.md 的压缩水位线，用于档案过大时的增量压缩。\n"
        "\n"
        f"推演累计轮次: 0\n"
        f"压缩阈值: {THRESHOLDS['compress_every']}\n"
        "上次推演时间: 从未\n"
        "上次压缩时间: 从未\n"
        "累计压缩次数: 0\n"
        "已压缩至行数: 0\n"
        "状态: 空闲\n"
        "备注: 初始化\n"
    )
    with FileLock(p):
        if not p.exists():
            atomic_write(p, text)


# --------------------------------------------------------------------------
# 摘要 / 档案体量
# --------------------------------------------------------------------------

def summary_stats() -> dict:
    p = SKILL_ROOT / FILES["summary"]
    text = read_text(p)
    return {
        "path": str(p),
        "exists": p.exists(),
        "chars": len(text),
        "lines": count_lines(p),
        "tokens_mid": est_tokens(text, "mid"),
        "tokens_high": est_tokens(text, "high"),
        # 闸门看 mid（中值）；high 只作预警，避免保守上界误判超限
        "over_cap": (
            est_tokens(text, "mid") > THRESHOLDS["summary_token_cap"]
            or len(text) > THRESHOLDS["summary_char_cap"]
        ),
        # 二次浓缩只看 token(mid)；字符数只作硬兜底，不再按 0.85 折算——
        # 摘要含大量 markdown / 拉丁 / 空白，字符密度与中文正文不同，折算会误报。
        "needs_recondense": (
            est_tokens(text, "mid") >= THRESHOLDS["summary_recondense_at"]
            or len(text) > THRESHOLDS["summary_char_cap"]
        ),
    }


def archive_stats() -> dict:
    p = SKILL_ROOT / FILES["archive"]
    text = read_text(p)
    return {
        "path": str(p),
        "bytes": len(text.encode("utf-8", errors="replace")),
        "chars": len(text),
        "lines": count_lines(p),
        "tokens_mid": est_tokens(text, "mid"),
        # 脚本读全量无成本（不进模型上下文），但压缩时是否全量送模型由 incremental_advised 决定
        "incremental_advised": len(text.encode("utf-8", errors="replace"))
        > THRESHOLDS["archive_incremental_bytes"],
    }


def read_head(path: Path, chars: int) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    with p.open("r", encoding="utf-8", errors="replace") as f:
        return f.read(chars)


# --------------------------------------------------------------------------
# 日志
# --------------------------------------------------------------------------

def append_log(event: str) -> None:
    p = SKILL_ROOT / FILES["log"]
    with FileLock(p):
        old = read_text(p)
        if not old.startswith("#"):
            old = (
                "# PHILOSOPHY_SUMMARY 压缩事件日志\n"
                "\n"
                "> 每次摘要压缩 / 二次浓缩 / 压缩失败均在此留痕。原始档案 PHILOSOPHY.md 只追加不删。\n"
                "\n"
            ) + old
        atomic_write(p, old.rstrip() + f"\n- {now_str()} | {event}\n")


# --------------------------------------------------------------------------
# 命令实现
# --------------------------------------------------------------------------

def cmd_status(_a) -> int:
    ensure_counter()
    c = read_counter()
    s = summary_stats()
    a = archive_stats()
    rounds = get_rounds()
    thr = int(re.search(r"\d+", c.get("压缩阈值", str(THRESHOLDS["compress_every"]))).group())
    print("== 推演记忆防膨胀状态 ==")
    print(f"轮次        : {rounds} / 阈值 {thr}  → {'【需压缩】' if rounds >= thr else '不压缩'}")
    print(f"状态        : {c.get('状态', '-')}")
    print(f"上次推演    : {c.get('上次推演时间', '-')}")
    print(f"上次压缩    : {c.get('上次压缩时间', '-')}（累计 {c.get('累计压缩次数', '0')} 次）")
    print(f"压缩水位线  : 第 {c.get('已压缩至行数', '0')} 行")
    print(f"摘要        : 存在={s['exists']} 字符={s['chars']} 行={s['lines']} "
          f"token≈{s['tokens_mid']}(上界{s['tokens_high']}) "
          f"→ {'超限违规' if s['over_cap'] else ('需二次浓缩' if s['needs_recondense'] else '正常')}")
    print(f"档案        : {a['bytes']} 字节 / {a['lines']} 行 "
          f"→ {'建议增量压缩' if a['incremental_advised'] else '可全量压缩'}")
    return 0


def cmd_get(_a) -> int:
    print(get_rounds())
    return 0


def cmd_incr(a) -> int:
    ensure_counter()
    with FileLock(counter_path()):
        n = get_rounds() + 1
        upd = {
            "推演累计轮次": str(n),
            "上次推演时间": now_str(),
            "状态": "空闲",
        }
        if a.note:
            upd["备注"] = a.note
        write_counter(upd)
    print(f"推演累计轮次 = {n}")
    if n >= THRESHOLDS["compress_every"]:
        print(">>> 已达阈值，请立即执行摘要压缩流程")
    return 0


def cmd_reset(_a) -> int:
    write_counter({"推演累计轮次": "0", "状态": "空闲"})
    print("推演累计轮次 已重置为 0")
    return 0


def cmd_should_compress(_a) -> int:
    return 0 if get_rounds() >= THRESHOLDS["compress_every"] else 1


def cmd_summary_check(_a) -> int:
    s = summary_stats()
    cap = THRESHOLDS["summary_token_cap"]
    if est_tokens(read_text(SKILL_ROOT / FILES["summary"]), "mid") > cap:
        print(f"摘要超限（token≈{s['tokens_mid']} > {cap}）：必须再浓缩，压到 {cap} 以内才允许继续推演")
        return 0
    if s["chars"] > THRESHOLDS["summary_char_cap"]:
        print(f"摘要超字符硬兜底（{s['chars']} > {THRESHOLDS['summary_char_cap']}）：必须再浓缩")
        return 0
    if est_tokens(read_text(SKILL_ROOT / FILES["summary"]), "mid") >= THRESHOLDS["summary_recondense_at"]:
        print(f"摘要逼近上限（token≈{s['tokens_mid']} ≥ {THRESHOLDS['summary_recondense_at']}）：本轮先做二次再浓缩")
        return 0
    print(f"摘要体量正常（token≈{s['tokens_mid']} / 字符 {s['chars']}；上限 {cap} token、{THRESHOLDS['summary_char_cap']} 字符）")
    return 1


def cmd_tokens(a) -> int:
    t = read_text(Path(a.file))
    print(json.dumps({
        "file": a.file,
        "chars": len(t),
        "mid": est_tokens(t, "mid"),
        "high": est_tokens(t, "high"),
        "low": est_tokens(t, "low"),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_archive_stats(_a) -> int:
    print(json.dumps(archive_stats(), ensure_ascii=False, indent=2))
    return 0


def cmd_prepare_compress(_a) -> int:
    ensure_counter()
    c = read_counter()
    a = archive_stats()
    s = summary_stats()
    wm = int(re.search(r"\d+", c.get("已压缩至行数", "0")).group())
    incremental = a["incremental_advised"] and wm > 0 and wm < a["lines"]
    plan = {
        "mode": "incremental" if incremental else "full",
        "reason": (
            f"档案 {a['bytes']} 字节 > {THRESHOLDS['archive_incremental_bytes']} 且存在水位线 {wm}"
            if incremental else
            ("档案未超阈值，按用户规则全量压缩" if not a["incremental_advised"] else "无有效水位线，首次须全量")
        ),
        "archive_lines": a["lines"],
        "watermark_line": wm,
        "start_line": (wm + 1) if incremental else 1,
        "summary_tokens_now": s["tokens_mid"],
        "token_cap": THRESHOLDS["summary_token_cap"],
        "instruction": (
            "【增量】只读 PHILOSOPHY.md 第 {start} 行至末行的新增部分，与现有摘要合并后覆盖写入摘要"
            if incremental else
            "【全量】读取 PHILOSOPHY.md 全部历史推演记录，与现有摘要合并后覆盖写入摘要"
        ),
        "hard_rules": [
            "只保留四板块：已确立核心观点 / 各方思想矛盾冲突点 / 尚未解决的开放问题 / 下一步推演方向",
            f"输出 ≤ {THRESHOLDS['summary_token_cap']} token（字符兜底 ≤ {THRESHOLDS['summary_char_cap']}）",
            "必须以现有 PHILOSOPHY_SUMMARY.md 的【已确立核心观点】为继承底本，防止旧观点被新内容挤掉",
            "原始档案 PHILOSOPHY.md 只追加不删，禁止任何形式清空",
        ],
    }
    plan["instruction"] = plan["instruction"].format(start=plan["start_line"])
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_compressed(a) -> int:
    c = read_counter()
    cnt = int(re.search(r"\d+", c.get("累计压缩次数", "0")).group()) + 1
    lines = a.lines if a.lines is not None else count_lines(SKILL_ROOT / FILES["archive"])
    write_counter({
        "推演累计轮次": "0",
        "上次压缩时间": now_str(),
        "累计压缩次数": str(cnt),
        "已压缩至行数": str(lines),
        "状态": "空闲",
    })
    append_log(f"压缩成功 #{cnt}（{'增量' if a.incremental else '全量'}，水位线 → 第 {lines} 行），轮次归零")
    print(f"已标记压缩完成：轮次归零，水位线={lines}，累计压缩 {cnt} 次")
    return 0


def cmd_compress_fail(a) -> int:
    """压缩失败：绝不静默重置计数——保持 ≥ 阈值，下一轮再试。"""
    rounds = get_rounds()
    write_counter({"状态": f"压缩失败待重试（{a.reason}）"})
    append_log(f"压缩失败（{a.reason}），轮次保持 {rounds} 不归零，下轮重试；旧摘要继续生效")
    print(f"已记录失败：轮次保持 {rounds}（不归零），旧摘要继续生效")
    return 1


def cmd_fragment(a) -> int:
    """有界局部检索：只返回命中处 ±context 行，且总字符数封顶。
    这是规则 3 中「调取局部原始片段佐证」的唯一合法通道。"""
    p = SKILL_ROOT / FILES["archive"]
    if not p.exists():
        print("档案不存在", file=sys.stderr)
        return 1
    lines = read_text(p).splitlines()
    hits = []
    try:
        pat = re.compile(a.pattern, re.IGNORECASE)
    except re.error as e:
        print(f"正则错误: {e}", file=sys.stderr)
        return 2
    for i, ln in enumerate(lines):
        if pat.search(ln):
            hits.append(i)
        if len(hits) >= a.max_hits:
            break
    if not hits:
        print("未命中任何片段。放宽关键词再试，或改用 prepare-compress 走全量压缩。")
        return 1
    ctx = a.context
    win = a.window
    spans = []
    for i in hits:
        lo, hi = max(0, i - ctx), min(len(lines), i + ctx + 1)
        if spans and lo <= spans[-1][1]:
            spans[-1][1] = hi
        else:
            spans.append([lo, hi])
    buf, total = [], 0

    def render(lo: int, hi: int) -> str:
        """整行渲染；若该行过长（推演日志常一行数千字），改为绕命中位置开窗。"""
        out = []
        for n in range(lo, hi):
            ln = lines[n]
            ms = list(pat.finditer(ln))
            if len(ln) <= win * 2 or not ms:
                out.append(f"{n + 1}: {ln}")
                continue
            pieces = []
            prev_end = 0
            for m in ms:
                s = max(prev_end, m.start() - win)
                e = min(len(ln), m.end() + win)
                if s > prev_end:
                    pieces.append("…")
                pieces.append(ln[s:e])
                prev_end = e
            if prev_end < len(ln):
                pieces.append("…")
            out.append(f"{n + 1}: [长行·按命中位置开窗] " + "".join(pieces))
        return "\n".join(out)

    for lo, hi in spans:
        chunk = render(lo, hi)
        if total + len(chunk) > a.max_chars:
            room = a.max_chars - total
            if room <= 0:
                break
            buf.append(chunk[:room] + "\n…[已达单次检索上限，截断]")
            total += room
            break
        buf.append(chunk)
        total += len(chunk)
    out = "\n…(片段间有省略)\n".join(buf)
    print(f"# 命中 {len(hits)} 处，返回 {len(spans)} 个片段，共 {total} 字符（上限 {a.max_chars}）\n")
    print(out)
    append_log(f"局部检索 pattern={a.pattern!r} → {len(hits)} 处命中 / {total} 字符")
    return 0


def cmd_log(a) -> int:
    append_log(a.event)
    print("已记录")
    return 0


# --------------------------------------------------------------------------
# 自检
# --------------------------------------------------------------------------

def cmd_selftest(_a) -> int:
    import shutil as _sh
    tmp = Path(tempfile.mkdtemp(prefix="dm_selftest_"))
    global SKILL_ROOT
    orig_root = SKILL_ROOT
    ok = True

    def check(name, cond, extra=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}{(' — ' + extra) if extra else ''}")
        if not cond:
            ok = False

    try:
        SKILL_ROOT = tmp

        print("== 1. 计数器初始化与持久化 ==")
        ensure_counter()
        check("run_counter.md 已创建", counter_path().exists())
        check("初始轮次为 0", get_rounds() == 0, f"实际 {get_rounds()}")

        print("== 2. incr 累加 + 重启后不丢（模拟定时任务重启） ==")
        for _ in range(4):
            cmd_incr(argparse.Namespace(note=None))
        check("累加 4 次 = 4", get_rounds() == 4, f"实际 {get_rounds()}")
        # 模拟进程重启：仅靠磁盘恢复
        check("重读磁盘仍为 4", get_rounds() == 4)
        cmd_incr(argparse.Namespace(note="T012"))
        check("第 5 轮后达到阈值", cmd_should_compress(None) == 0)

        print("== 3. 阈值分支 ==")
        cmd_reset(None)
        check("归零后不该压缩", cmd_should_compress(None) == 1)

        print("== 4. token 估算单调性与量级 ==")
        t_cjk = "哲" * 1000
        t_en = ("word " * 1000).strip()
        c, e = est_tokens(t_cjk), est_tokens(t_en)
        check("中文 1000 字落在 600–1400", 600 <= c <= 1400, f"{c}")
        check("英文 1000 词落在 1000–1800", 1000 <= e <= 1800, f"{e}")
        check("上界 ≥ 中值 ≥ 下界",
              est_tokens(t_cjk, "high") >= c >= est_tokens(t_cjk, "low"))
        check("空串为 0", est_tokens("") == 0)

        print("== 5. 摘要闸门 ==")
        atomic_write(tmp / FILES["summary"],
                     "【已确立核心观点】\n" + "测试内容" * 1200)
        s = summary_stats()
        check("超长摘要判定需二次浓缩", s["needs_recondense"], f"token≈{s['tokens_mid']}")
        check("summary-check 返回 0", cmd_summary_check(None) == 0)
        atomic_write(tmp / FILES["summary"], "【已确立核心观点】\n极短摘要。")
        check("短摘要判定正常", cmd_summary_check(None) == 1)

        print("== 6. 压缩计划：全量 vs 增量 ==")
        atomic_write(tmp / FILES["archive"], "\n".join(f"第{i}行推演记录" for i in range(1, 201)))
        plan_full = json.loads(_capture(cmd_prepare_compress, None))
        check("小档案 → full 模式", plan_full["mode"] == "full", plan_full["reason"])
        big = "推演" * (THRESHOLDS["archive_incremental_bytes"] // 2 + 100)
        atomic_write(tmp / FILES["archive"], big + "\n" + "\n".join(f"第{i}行" for i in range(300)))
        write_counter({"已压缩至行数": "5"})
        plan_inc = json.loads(_capture(cmd_prepare_compress, None))
        check("大档案+水位线 → incremental", plan_inc["mode"] == "incremental", plan_inc["reason"])
        check("增量起点 = 水位线+1", plan_inc["start_line"] == 6, str(plan_inc["start_line"]))

        print("== 7. mark-compressed 与 compress-fail ==")
        cmd_mark_compressed(argparse.Namespace(lines=1234, incremental=False))
        c2 = read_counter()
        check("轮次归零", get_rounds() == 0)
        check("水位线写入", c2["已压缩至行数"] == "1234", c2.get("已压缩至行数", ""))
        check("累计压缩次数 +1", c2["累计压缩次数"] == "1", c2.get("累计压缩次数", ""))
        cmd_incr(argparse.Namespace(note=None))
        cmd_incr(argparse.Namespace(note=None))
        cmd_incr(argparse.Namespace(note=None))
        cmd_incr(argparse.Namespace(note=None))
        cmd_incr(argparse.Namespace(note=None))
        r_before = get_rounds()
        rc = cmd_compress_fail(argparse.Namespace(reason="测试性失败"))
        check("失败不归零", get_rounds() == r_before, f"{r_before} → {get_rounds()}")
        check("失败退出码非 0", rc != 0)

        print("== 8. 局部检索有界 ==")
        atomic_write(tmp / FILES["archive"],
                     "\n".join([f"无关行 {i}" for i in range(50)]
                               + ["关键行：宽恕与报的挂载回路"]
                               + [f"无关行 {i}" for i in range(50)]))
        out = _capture(cmd_fragment, argparse.Namespace(
            pattern="挂载回路", context=2, window=300, max_chars=500, max_hits=5))
        whole = read_text(tmp / FILES["archive"])
        check("命中目标片段", "挂载回路" in out)
        check("返回体受限（≤ max_chars + 头信息）", len(out) < 900, f"{len(out)} 字符")
        check("远处的行未被返回（未加载全量）", "无关行 25" not in out)
        check("返回量远小于档案", len(out) * 4 < len(whole), f"{len(out)} vs {len(whole)}")

        print("== 9. 原子写并发不丢计数 ==")
        atomic_write(tmp / FILES["counter"],
                     "# c\n推演累计轮次: 0\n压缩阈值: 5\n已压缩至行数: 0\n")
        for _ in range(10):
            cmd_incr(argparse.Namespace(note=None))
        check("串行 10 次 = 10", get_rounds() == 10, f"实际 {get_rounds()}")

        print("== 10. 事件日志 ==")
        check("日志已生成", (tmp / FILES["log"]).exists())
    finally:
        SKILL_ROOT = orig_root
        _sh.rmtree(tmp, ignore_errors=True)

    print("\n== 自检结果 ==")
    print("全部通过 ✅" if ok else "存在失败项 ❌")
    return 0 if ok else 1


def _capture(fn, arg) -> str:
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn(arg)
    return buf.getvalue()


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="deduction_memory.py",
        description="觉思者 · 推演记忆防膨胀工具（轮次持久化 + 摘要体量闸门）",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="总览").set_defaults(func=cmd_status)
    sub.add_parser("get", help="当前轮次").set_defaults(func=cmd_get)

    q = sub.add_parser("incr", help="完成一轮后 +1")
    q.add_argument("--note", default=None)
    q.set_defaults(func=cmd_incr)

    sub.add_parser("reset", help="轮次归零").set_defaults(func=cmd_reset)
    sub.add_parser("should-compress", help="该压缩则 exit 0").set_defaults(func=cmd_should_compress)
    sub.add_parser("summary-check", help="摘要是否需二次浓缩").set_defaults(func=cmd_summary_check)

    t = sub.add_parser("tokens", help="确定性 token 估算")
    t.add_argument("file")
    t.add_argument("--mode", default="mid", choices=["mid", "high", "low"])
    t.set_defaults(func=cmd_tokens)

    sub.add_parser("archive-stats", help="档案体量").set_defaults(func=cmd_archive_stats)
    sub.add_parser("prepare-compress", help="压缩执行计划 JSON").set_defaults(func=cmd_prepare_compress)

    m = sub.add_parser("mark-compressed", help="压缩成功后登记")
    m.add_argument("--lines", type=int, default=None, help="已覆盖到的档案行数")
    m.add_argument("--incremental", action="store_true")
    m.set_defaults(func=cmd_mark_compressed)

    f = sub.add_parser("compress-fail", help="压缩失败登记（不归零）")
    f.add_argument("--reason", default="未说明")
    f.set_defaults(func=cmd_compress_fail)

    g = sub.add_parser("fragment", help="有界局部检索（禁止全量）")
    g.add_argument("--pattern", required=True)
    g.add_argument("--context", type=int, default=1, help="命中行上下各取 N 行")
    g.add_argument("--window", type=int, default=300,
                   help="命中行过长时，绕命中位置左右各取 N 字符（推演日志常一行数千字）")
    g.add_argument("--max-chars", type=int, default=THRESHOLDS["fragment_max_chars"])
    g.add_argument("--max-hits", type=int, default=20)
    g.set_defaults(func=cmd_fragment)

    lg = sub.add_parser("log", help="追加事件日志")
    lg.add_argument("--event", required=True)
    lg.set_defaults(func=cmd_log)

    sub.add_parser("selftest", help="内建测试").set_defaults(func=cmd_selftest)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except SystemExit:
        raise
    except Exception as e:  # 明确报错，不静默
        print(f"[deduction_memory] 错误: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
