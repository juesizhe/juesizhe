# -*- coding: utf-8 -*-
import re, os
BASE = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"

def show(path, lineno, head=0, tail=0, label=""):
    p = os.path.join(BASE, path)
    lines = open(p, 'rb').read().decode('utf-8').split('\n')
    ln = lines[lineno - 1]
    s = ln.strip()
    if head:
        print(f"[{label or path} L{lineno} HEAD] {s[:head]}")
    if tail:
        print(f"[{label or path} L{lineno} TAIL] ...{s[-tail:]}")
    print()

def find(path, rx, head=0, tail=0, limit=6):
    p = os.path.join(BASE, path)
    lines = open(p, 'rb').read().decode('utf-8').split('\n')
    n = 0
    for i, ln in enumerate(lines, 1):
        if re.search(rx, ln):
            n += 1
            if n > limit:
                break
            s = ln.strip()
            if head:
                print(f"[{path} L{i} HEAD] {s[:head]}")
            if tail:
                print(f"[{path} L{i} TAIL] ...{s[-tail:]}")
            print()

print("### SKILL.md")
show("SKILL.md", 84, head=260)
show("SKILL.md", 232, tail=200)
show("SKILL.md", 233, tail=200)
show("SKILL.md", 234, tail=100)

print("### core/part-01.md")
show("core/part-01.md", 9, head=400)
show("core/part-01.md", 10, tail=200)
show("core/part-01.md", 11, tail=200)

print("### CORE.md 分工说明末项 / 域行 / 映射尾")
find("CORE.md", r"共 \*\*\d+ 项|可编辑项 \*\*\d+ 类", tail=300, limit=5)
find("CORE.md", r"关系 · 公共域", tail=300, limit=5)
show("CORE.md", 165, tail=300)
show("CORE.md", 166, tail=300)
show("CORE.md", 164, tail=200)

print("### core/part-04.md 尾部")
show("core/part-04.md", 43, tail=300)
show("core/part-04.md", 44, tail=300)
show("core/part-04.md", 45, tail=300)
