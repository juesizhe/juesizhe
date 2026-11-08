#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加摘要版本日志（该文件为 LF，不在 preflight MANAGED 名单）"""
import os

ROOT = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
P = os.path.join(ROOT, "PHILOSOPHY_SUMMARY.log.md")

with open(P, "rb") as f:
    b = f.read()
assert b.count(b"\r\n") == 0, "该文件应为 LF，实测出现 CRLF，须停手复核"
t = b.decode("utf-8")
if "v31" in t:
    print("SKIP: 摘要日志已含 v31")
else:
    line = ("- 2026-11-03T00:15:59+0800 · v31（自选「疑与信」→ P98／C97 入 core/part-05.md 认知 · 语言 · 技术域；"
            "5183 → 4677 字符，token 3566 → 3128；整份重写：总纲链删旧枚举、P70–P91 段删四项、心律段并旧条、"
            "Q 清单精简并补 P98 三问；先压旧段再写新段）\n")
    if not t.endswith("\n"):
        t += "\n"
    t += line
    with open(P, "wb") as f:
        f.write(t.encode("utf-8"))
    print("OK 摘要日志追加 v31（LF）")
