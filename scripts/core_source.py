# -*- coding: utf-8 -*-
"""觉思者 · 纲要（CORE）多卷加载器 —— 分册后的唯一拼接入口（2026-10-27 建成）

背景
====
`CORE.md` 单文件 2026-10-27 已达 307KB（预算 300KB），且其中 257KB 是「核心纲要」
区的 82 条条目正文。**经用户裁定，2026-10-27 起按域分册**：

    CORE.md            文件头 / 总纲 / 分册导航 / 分工说明 / 来源映射
    core/part-01.md    ……按 domain 拆出的七卷正文（- **Cn …** 条目）

设计原则
========
**逻辑上仍是一份文档**。本模块把七卷拼回 `## 核心纲要` 与 `## 分工说明` 之间的原位，
使所有既有解析规则（行首 `- **Cn`、`### 域（…）`、分工说明区、来源映射区的位置关系）
与分册前**完全一致**——这样 `preflight.py` / `build_deduce.py` /
`check_core_domains.py` 都不必改解析逻辑，只改「从哪读」。

纪律
====
- 只读不写：本模块绝不修改任何权威源。
- 卷文件名必须匹配 `core/part-\\d+\\.md`，按文件名排序即为逻辑顺序。
- 唯一例外情形：`core/` 目录不存在时，退化为只读 `CORE.md`（保证脚本在回滚状态下不炸）。
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EOL = "\r\n"

CORE_FILE = "CORE.md"
CORE_DIR = "core"
PART_RE = re.compile(r"^part-\d+\.md$")

ENTRY_HEAD = "## 核心纲要"
WORK_HEAD = "## 分工说明"
MAP_HEAD = "## 来源映射"


def core_path():
    return os.path.join(ROOT, CORE_FILE)


def part_rel_paths():
    """各卷相对路径，按文件名排序（part-01 → part-07）。"""
    d = os.path.join(ROOT, CORE_DIR)
    if not os.path.isdir(d):
        return []
    return [os.path.join(CORE_DIR, f).replace(os.sep, "/")
            for f in sorted(os.listdir(d)) if PART_RE.match(f)]


def read_lines(rel):
    with io.open(os.path.join(ROOT, rel), "rb") as f:
        return f.read().decode("utf-8").split(EOL)


def core_file_lines():
    return read_lines(CORE_FILE)


def part_lines():
    """七卷正文（去掉每个卷文件尾部的多余空行后依次拼接）。"""
    out = []
    for rel in part_rel_paths():
        ls = read_lines(rel)
        while ls and ls[-1] == "":
            ls.pop()
        if out:
            out.append("")
        out.extend(ls)
    return out


def lines():
    """返回逻辑整文档的行列表（顺序与分册前完全一致）。"""
    core = core_file_lines()
    try:
        work_i = next(i for i, l in enumerate(core) if l.startswith(WORK_HEAD))
    except StopIteration:
        work_i = len(core)
    body = part_lines()
    if not body:
        return core
    head, tail = core[:work_i], core[work_i:]
    if not head or head[-1] != "":
        head = head + [""]
    return head + body + [""] + tail


def text():
    """逻辑整文档的文本（行尾 CRLF，与权威源同口径）。"""
    return EOL.join(lines())


def sizes():
    """[(相对路径, 字节)]：CORE.md 在前，各卷按序号在后。"""
    out = []
    p = core_path()
    if os.path.exists(p):
        out.append((CORE_FILE, os.path.getsize(p)))
    for rel in part_rel_paths():
        fp = os.path.join(ROOT, rel)
        if os.path.exists(fp):
            out.append((rel, os.path.getsize(fp)))
    return out


def total_kb():
    return sum(s for _, s in sizes()) / 1024


def max_part_kb():
    parts = sizes()[1:]
    return (max(s for _, s in parts) / 1024) if parts else 0.0


if __name__ == "__main__":
    n_entries = len(re.findall(r"^- \*\*C\d+", "\n".join(lines()), re.M))
    print("卷数 %d ／ 条目 %d ／ CORE.md+七卷合计 %.1fKB ／ 最大单卷 %.1fKB"
          % (len(part_rel_paths()), n_entries, total_kb(), max_part_kb()))
    for rel, sz in sizes():
        print("  %-22s %8dB (%.1fKB)" % (rel, sz, sz / 1024))
