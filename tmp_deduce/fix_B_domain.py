#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补：CORE.md 认知域分工说明行的枚举（标题-only 缺 C97）"""
import os

ROOT = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
P = os.path.join(ROOT, "CORE.md")

with open(P, "rb") as f:
    b = f.read()
crlf = b.count(b"\r\n")
lf = b.count(b"\n")
eol = "\r\n" if (lf > 0 and crlf == lf) else "\n"
t = b.decode("utf-8")

old = "、C93**："
if "、C93、C97**：" in t:
    print("SKIP: 分工说明行枚举已含 C97")
else:
    assert t.count(old) == 1, "锚点不唯一: %d" % t.count(old)
    t = t.replace(old, "、C93、C97**：", 1)
    with open(P, "wb") as f:
        f.write(t.encode("utf-8"))
    print("OK CORE 分工说明行枚举 +C97")
