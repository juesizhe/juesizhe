#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觉思者 · 写盘前门禁（scripts/preflight.py）

职责
====
把 2026-10-12 ~ 10-21 推演周期里**真实发生过的事故**固化为确定性机检，
任何一场推演 / 精炼 / 压缩**写盘之前**必须先过本门禁；不过则不许写。

门禁清单（全部硬门禁，除标注「预警」者外，不过即 exit 1）：

  G-EOL   行尾完整性：托管文件不得含裸 CR（\\r 后不跟 \\n）；主行尾在全文件内一致。
          （事故源：2026-10-14 SKILL.md 被写成裸 CR 致行粘连、2026-10-19 CORE.md 行尾事故、
           当前 PHILOSOPHY.md 与 tuiyan_pool_state.md 仍残留 3 处 \\r\\r\\n）
  G-MARK  SKILL.md 的 AUTO_EVOLVE_START / END 标记必须恰好各一个且 START 在前；
          YAML frontmatter 首行必须是 `---`（事故源：2026-10-14 frontmatter 被写成带反斜杠的 ---）。
  G-NUM   命题编号连续性：AUTO_EVOLVE 区内 P 编号无重复、无缺号（RETIRED 白名单除外）。
  G-COUNT 命题库与纲要计数一致：CORE.md 的 C 条数 == 存活 P 条数，且 C 的来源映射
          覆盖的 P 集合 == 存活 P ∪ 已合并 P（双射）。
          （事故源：P16/P18 撞号、CORE 与 SKILL 计数 39/46/49 不同步）
  G-INDEX 派生索引新鲜度：prompts/deduce.md 与 core_index.md 的条目数必须与权威源一致。
          （事故源：采纳后忘记重跑 build_deduce.py，载荷索引滞后）
  G-SUM   摘要体量：PHILOSOPHY_SUMMARY.md ≤ 5200 字符（硬）；≥90% 上限预警。
          （事故源：5218>5200 触发二次再浓缩，白跑一轮浓缩）
  G-BUDGET 资产体量预算（仅预警，不拦截）：SKILL.md ≤ 600KB、CORE.md ≤ 300KB、
          PHILOSOPHY.md ≤ 600KB。超限只提示该做结构性压缩，不阻断写盘。

用法
====
  python scripts/preflight.py                 # 全部门禁
  python scripts/preflight.py --gate EOL NUM  # 只跑指定门禁
  python scripts/preflight.py --repair-eol    # 先修复裸 CR（自动备份）再跑门禁
  python scripts/preflight.py --quiet         # 只输出失败项

退出码：0 = 全部通过（可以写盘）；1 = 有硬门禁未过（禁止写盘）；2 = 用法错误。

设计原则（与 contrib_check.py 一致）
==================================
- 纯函数 + 显式规则表，绝不调用模型。
- 修裸 CR 是唯一允许的自动修复，且只做「\\r\\r\\n → \\r\\n」与「行首/行尾孤立 \\r 删除」，
  绝不触碰任何其他字节；修复前必须备份到 .workbuddy/bak/preflight_<时间戳>/。
- 本脚本只读不写（除 --repair-eol），不替代任何权威源。
"""
import argparse
import os
import re
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANAGED = [
    "SKILL.md",
    "CORE.md",
    "PHILOSOPHY.md",
    "PHILOSOPHY_SUMMARY.md",
    "prompts/deduce.md",
    "prompts/core_index.md",
    "references/tuiyan_pool_state.md",
    "references/evidence_ledger.md",
    "references/tuiyan_corpus.md",
    "references/canon.md",
]

# 已合并、编号不回收的历史缺号（P3→C1、P10→C9；内容全留，见蒸馏日志）
RETIRED_P = {3, 10}

THRESHOLDS = {
    "summary_char_cap": 5200,       # 硬兜底（与 deduction_memory.py 一致）
    "summary_warn_ratio": 0.90,     # 达到 90% 即预警
    "skill_budget_kb": 600,
    "core_budget_kb": 300,
    "phil_budget_kb": 600,
}

START = "<!-- AUTO_EVOLVE_START -->"
END = "<!-- AUTO_EVOLVE_END -->"


# ─────────────────────────── 工具函数 ───────────────────────────

def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def eol_scan(path):
    """返回 (crlf, lf, bare_cr, dominant_eol)。按字节扫，不经 universal newlines。"""
    with open(path, "rb") as f:
        b = f.read()
    crlf = b.count(b"\r\n")
    bare = len(re.findall(rb"\r(?!\n)", b))
    lf = b.count(b"\n") - crlf
    dominant = "CRLF" if crlf >= lf else "LF"
    return crlf, lf, bare, dominant


def parse_p_ids(skill_text):
    if START not in skill_text or END not in skill_text:
        return None
    block = skill_text.split(START, 1)[1].split(END, 1)[0]
    ids = []
    for line in block.splitlines():
        m = re.match(r"^\s*-\s+(P\d+)\b", line)
        if m:
            ids.append(int(m.group(1)[1:]))
    return ids


def parse_c_entries(core_text):
    """返回 [(cid, title, tail)]，tail 含来源映射。"""
    out = []
    for line in core_text.splitlines():
        m = re.match(r"^\s*-\s+\*\*(C\d+)\s+([^*]+)\*\*\s*(.*)$", line)
        if m:
            out.append((int(m.group(1)[1:]), m.group(2).strip(), m.group(3)))
    return out


def est_tokens(text):
    """与 deduction_memory.py 同口径的中值估算：CJK 0.9 / 拉丁词 1.3 / 其他 0.5。"""
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+", text))
    other = len(re.findall(r"[^\sA-Za-z0-9\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", text))
    return int(cjk * 0.9 + latin * 1.3 + other * 0.5)


# ─────────────────────────── 门禁实现 ───────────────────────────

def gate_eol():
    rows, bad = [], []
    for rel in MANAGED:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            rows.append((rel, "缺失", "FAIL", "文件不存在"))
            bad.append(rel)
            continue
        crlf, lf, bare, dom = eol_scan(p)
        if bare:
            rows.append((rel, f"CRLF={crlf} LF={lf} 裸CR={bare}", "FAIL", f"含 {bare} 处裸 CR（潜伏行粘连）"))
            bad.append(rel)
        elif crlf and lf:
            rows.append((rel, f"CRLF={crlf} LF={lf} 裸CR=0", "FAIL", "行尾混用（CRLF 与 LF 并存）"))
            bad.append(rel)
        else:
            rows.append((rel, f"{dom}×{crlf + lf} 裸CR=0", "PASS", ""))
    return rows, bad


def gate_mark():
    p = os.path.join(ROOT, "SKILL.md")
    if not os.path.exists(p):
        return [("SKILL.md", "缺失", "FAIL", "文件不存在")], ["SKILL.md"]
    raw = open(p, "rb").read()
    text = raw.decode("utf-8", errors="replace")
    rows, bad = [], []
    n_start = text.count(START)
    n_end = text.count(END)
    if n_start == 1 and n_end == 1 and text.find(START) < text.find(END):
        rows.append(("AUTO_EVOLVE 标记", "各 1 处且 START 在前", "PASS", ""))
    else:
        rows.append(("AUTO_EVOLVE 标记", f"START×{n_start} END×{n_end}", "FAIL", "标记缺失/重复/顺序错"))
        bad.append("mark")
    head = raw[:400].decode("utf-8", errors="replace")
    first_line = head.splitlines()[0] if head.splitlines() else ""
    if first_line.strip() == "---" and "name: philosopher-sage" in head:
        rows.append(("YAML frontmatter", "首行 --- 且含 name", "PASS", ""))
    else:
        rows.append(("YAML frontmatter", f"首行={first_line.strip()[:20]!r}", "FAIL", "frontmatter 损坏（参考 10-14 事故）"))
        bad.append("frontmatter")
    return rows, bad


def gate_num():
    p = os.path.join(ROOT, "SKILL.md")
    if not os.path.exists(p):
        return [("命题编号", "缺失", "FAIL", "SKILL.md 不存在")], ["num"]
    ids = parse_p_ids(read_text(p))
    if ids is None:
        return [("命题编号", "无标记区", "FAIL", "AUTO_EVOLVE 标记缺失")], ["num"]
    rows, bad = [], []
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        rows.append(("重复编号", str(dups), "FAIL", "同号多条"))
        bad.append("num")
    mx = max(ids) if ids else -1
    missing = [i for i in range(0, mx + 1) if i not in ids and i not in RETIRED_P]
    if missing:
        rows.append(("缺号", str(missing), "FAIL", f"非白名单缺号（白名单={sorted(RETIRED_P)}）"))
        bad.append("num")
    if not bad:
        rows.append((f"P0–P{mx}", f"{len(ids)} 条存活 / 缺号仅白名单 {sorted(RETIRED_P)}", "PASS", ""))
    return rows, bad


def gate_count():
    sp = os.path.join(ROOT, "SKILL.md")
    cp = os.path.join(ROOT, "CORE.md")
    if not (os.path.exists(sp) and os.path.exists(cp)):
        return [("命题↔纲要计数", "文件缺失", "FAIL", "SKILL.md 或 CORE.md 不存在")], ["count"]
    ids = parse_p_ids(read_text(sp))
    centries = parse_c_entries(read_text(cp))
    live = {i for i in ids if i not in RETIRED_P}
    rows, bad = [], []
    cids = [c for c, _, _ in centries]
    cdups = sorted({c for c in cids if cids.count(c) > 1})
    if cdups:
        rows.append(("纲要重复编号", str(cdups), "FAIL", "同号多条"))
        bad.append("count")
    if len(cids) != len(live):
        rows.append(("条数一致", f"P 存活 {len(live)} vs C {len(cids)}", "FAIL", "命题库与纲要条数不等"))
        bad.append("count")
    referenced = set()
    for _, _, tail in centries:
        for pm in re.findall(r"P\d+", tail):
            referenced.add(int(pm[1:]))
    expected = live | RETIRED_P
    if referenced != expected:
        only_ref = sorted(referenced - expected)
        only_exp = sorted(expected - referenced)
        rows.append(("来源映射双射", f"多引 {only_ref} / 漏引 {only_exp}", "FAIL", "C 的来源映射与命题库不对应"))
        bad.append("count")
    if not bad:
        rows.append((f"P {len(live)} 条 ↔ C {len(cids)} 条", "双射成立（含合并号 "
                     + str(sorted(RETIRED_P)) + "）", "PASS", ""))
    return rows, bad


def gate_index():
    rows, bad = [], []
    # deduce.md 索引条数
    dp = os.path.join(ROOT, "prompts", "deduce.md")
    cp = os.path.join(ROOT, "prompts", "core_index.md")
    sp = os.path.join(ROOT, "SKILL.md")
    if not (os.path.exists(dp) and os.path.exists(sp)):
        rows.append(("派生索引", "文件缺失", "FAIL", "deduce.md 或 SKILL.md 不存在"))
        return rows, ["index"]
    ids = parse_p_ids(read_text(sp))
    live_n = len([i for i in ids if i not in RETIRED_P])
    deduce = read_text(dp)
    m = re.search(r"命题库索引\s*(\d+)\s*条", deduce)
    declared = int(m.group(1)) if m else -1
    sec9 = deduce.split("## 9 · 命题库索引", 1)[-1].split("## 10", 1)[0]
    actual = len(re.findall(r"^\s*-\s+\*\*P\d+\*\*", sec9, re.M))
    if declared != live_n or actual != live_n:
        rows.append(("deduce.md 索引", f"声明 {declared} / 实列 {actual} / 权威 {live_n}", "FAIL",
                     "索引滞后——采纳新命题后必须重跑 build_deduce.py"))
        bad.append("index")
    else:
        rows.append(("deduce.md 索引", f"{actual} 条 == 权威 {live_n}", "PASS", ""))
    # core_index.md
    if os.path.exists(cp):
        core = read_text(os.path.join(ROOT, "CORE.md"))
        c_n = len(parse_c_entries(core))
        ci = read_text(cp)
        m2 = re.search(r"共\s*(\d+)\s*条", ci)
        ci_declared = int(m2.group(1)) if m2 else -1
        ci_actual = len(re.findall(r"^\s*-\s+\*\*C\d+\*\*", ci, re.M))
        if ci_declared != c_n or ci_actual != c_n:
            rows.append(("core_index.md 索引", f"声明 {ci_declared} / 实列 {ci_actual} / 权威 {c_n}", "FAIL",
                         "索引滞后——必须重跑 build_deduce.py"))
            bad.append("index")
        else:
            rows.append(("core_index.md 索引", f"{ci_actual} 条 == 权威 {c_n}", "PASS", ""))
    return rows, bad


def gate_sum():
    p = os.path.join(ROOT, "PHILOSOPHY_SUMMARY.md")
    if not os.path.exists(p):
        return [("摘要体量", "缺失", "FAIL", "PHILOSOPHY_SUMMARY.md 不存在")], ["sum"]
    text = read_text(p)
    chars = len(text)
    cap = THRESHOLDS["summary_char_cap"]
    tok = est_tokens(text)
    if chars > cap:
        return [(f"摘要 {chars} 字符", f"上限 {cap}", "FAIL", "超限——先二次再浓缩才允许推演")], ["sum"]
    if chars >= cap * THRESHOLDS["summary_warn_ratio"]:
        return [(f"摘要 {chars} 字符", f"上限 {cap}（{chars * 100 // cap}%）", "WARN",
                 f"逼近上限；token≈{tok}")], []
    return [(f"摘要 {chars} 字符", f"上限 {cap}；token≈{tok}", "PASS", "")], []


def gate_budget():
    rows = []
    for rel, key in [("SKILL.md", "skill_budget_kb"), ("CORE.md", "core_budget_kb"),
                     ("PHILOSOPHY.md", "phil_budget_kb")]:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        kb = os.path.getsize(p) / 1024
        limit = THRESHOLDS[key]
        if kb > limit:
            rows.append((rel, f"{kb:.0f}KB / 预算 {limit}KB", "WARN", "超预算——安排结构性压缩"))
        else:
            rows.append((rel, f"{kb:.0f}KB / 预算 {limit}KB", "PASS", ""))
    return rows, []


# ─────────────────────────── 裸 CR 修复（唯一自动修复） ───────────────────────────

def repair_eol():
    fixed = []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(ROOT, ".workbuddy", "bak", f"preflight_{stamp}")
    for rel in MANAGED:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        with open(p, "rb") as f:
            b = f.read()
        if not re.search(rb"\r(?!\n)", b):
            continue
        nb = re.sub(rb"\r\r\n", b"\r\n", b)          # 双 CR 归一
        nb = re.sub(rb"\r(?!\n)", b"", nb)            # 残余孤立 CR 删除
        if nb != b:
            os.makedirs(bak, exist_ok=True)
            shutil.copy2(p, os.path.join(bak, rel.replace("/", "_")))
            with open(p, "wb") as f:
                f.write(nb)
            fixed.append(rel)
    return fixed, bak


# ─────────────────────────── 主流程 ───────────────────────────

GATES = {
    "EOL": ("行尾完整性", gate_eol),
    "MARK": ("标记与 frontmatter", gate_mark),
    "NUM": ("命题编号连续性", gate_num),
    "COUNT": ("命题↔纲要计数", gate_count),
    "INDEX": ("派生索引新鲜度", gate_index),
    "SUM": ("摘要体量", gate_sum),
    "BUDGET": ("资产预算（预警）", gate_budget),
}


def main():
    ap = argparse.ArgumentParser(description="觉思者写盘前门禁")
    ap.add_argument("--gate", nargs="+", choices=list(GATES), help="只跑指定门禁（默认全跑）")
    ap.add_argument("--repair-eol", action="store_true", help="先修复裸 CR（自动备份）再跑门禁")
    ap.add_argument("--quiet", action="store_true", help="只输出非 PASS 行")
    a = ap.parse_args()

    if a.repair_eol:
        fixed, bak = repair_eol()
        if fixed:
            print(f"[repair] 已修复裸 CR：{', '.join(fixed)}")
            print(f"[repair] 备份至 {os.path.relpath(bak, ROOT)}")
        else:
            print("[repair] 未发现裸 CR，无需修复")

    names = a.gate or list(GATES)
    all_rows, failed = [], []
    for g in names:
        title, fn = GATES[g]
        rows, bad = fn()
        all_rows.append((g, title, rows))
        if bad:
            failed.append(g)

    print("=" * 78)
    print("觉思者 · 写盘前门禁（preflight）")
    print("=" * 78)
    for g, title, rows in all_rows:
        print(f"\n▌G-{g} {title}")
        for name, state, status, note in rows:
            if a.quiet and status == "PASS":
                continue
            mark = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}[status]
            line = f"  {mark} {name:<24s} {state}"
            if note:
                line += f"  —— {note}"
            print(line)

    print("\n" + "-" * 78)
    if failed:
        print(f"结论：✗ 未通过（{'、'.join('G-' + f for f in failed)}）——禁止写盘，先修复再写")
        sys.exit(1)
    print("结论：✓ 全部硬门禁通过——允许写盘")
    sys.exit(0)


if __name__ == "__main__":
    main()
