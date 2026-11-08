#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""摘要行尾归一（Write 工具产出 LF → 托管文件须 CRLF）并报告体量"""
import os

ROOT = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
P = os.path.join(ROOT, "PHILOSOPHY_SUMMARY.md")

with open(P, "rb") as f:
    b = f.read()
b = b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
with open(P, "wb") as f:
    f.write(b)

t = b.decode("utf-8")
lines = t.split("\r\n")
print("CRLF =", b.count(b"\r\n"), " LF =", b.count(b"\n"))
print("preflight 口径字符 =", len(t), "（硬顶 5200）")
print("文本模式字符 =", len(t) - b.count(b"\r\n"), " 行数 =", len(lines))
assert b.count(b"\r\n") == b.count(b"\n"), "行尾不纯"
assert len(t) <= 5200, "超硬顶"
