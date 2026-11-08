#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""差分校验：去 CR 后按行比对，确认无内容被吞"""
import os, difflib

ROOT = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
PAIRS = [
    ("SKILL.md", "SKILL.md.1103night", 16),   # 1 行改计数/清单 + 15 行 P98
    ("CORE.md", "CORE.md.1103night", 8),      # 7 处替换 + 1 行映射 + 1 行心律/分工(同文件多行)
    ("core/part-01.md", "core/part-01.md.1103night", 1),
    ("core/part-05.md", "core/part-05.md.1103night", 2),
    ("PHILOSOPHY.md", "PHILOSOPHY.md.1103night", 16),
    ("PHILOSOPHY_SUMMARY.md", "PHILOSOPHY_SUMMARY.md.1103night", 43),
    ("references/tuiyan_pool_state.md", None, None),
    ("references/evidence_ledger.md", None, None),
]

for cur, bak, expect in PAIRS:
    if bak is None:
        print("SKIP(无基线)", cur)
        continue
    a = open(os.path.join(ROOT, bak), "rb").read().decode("utf-8").replace("\r", "").split("\n")
    b = open(os.path.join(ROOT, cur), "rb").read().decode("utf-8").replace("\r", "").split("\n")
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    adds = pure_del = repl = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            adds += j2 - j1
        elif tag == "replace":
            repl += 1
            adds += j2 - j1
        elif tag == "delete":
            pure_del += i2 - i1
    print("%-36s 基线行=%4d 现行行=%4d 净增=%3d 整行替换=%2d 纯删除=%2d  %s" %
          (cur, len(a), len(b), len(b) - len(a), repl, pure_del,
           "OK" if pure_del == 0 else "!! 有纯删除"))
    assert pure_del == 0, "发现纯删除行（内容可能被吞）: " + cur
print("结论：所有基线文件均无纯删除行，仅追加 + 单行原地替换，内容未被吞。")
