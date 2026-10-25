#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 P37/P38/P39 三条追加进 SKILL.md 的 AUTO_EVOLVE 区（只追加，不改动其它章节）。"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "SKILL.md")
START = "<!-- AUTO_EVOLVE_START -->"
END = "<!-- AUTO_EVOLVE_END -->"

text = open(SKILL, encoding="utf-8").read()
assert START in text and END in text, "AUTO_EVOLVE 标记缺失"

head, rest = text.split(START, 1)
block, tail = rest.split(END, 1)

entries = []
for name in ("p37_entry.txt", "p38_entry.txt", "p39_entry.txt"):
    p = os.path.join(ROOT, ".workbuddy", name)
    entries.append(open(p, encoding="utf-8").read().strip())

new_block = block.rstrip("\n") + "\n" + "\n".join(entries) + "\n"
out = head + START + new_block + END + tail
open(SKILL, "w", encoding="utf-8", newline="") .write(out)
print("OK: 追加 3 条命题，文件大小", len(out))
for e in entries:
    print("  -", e[:12].replace("- ", "").strip())
