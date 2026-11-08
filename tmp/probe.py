# -*- coding: utf-8 -*-
import re, io, os
BASE = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"

def probe(path, patterns, tail=0):
    p = os.path.join(BASE, path)
    b = open(p, 'rb').read()
    eol = 'CRLF' if b.count(b'\r\n') > b.count(b'\n') - b.count(b'\r\n') else 'LF'
    lines = b.decode('utf-8').split('\n')
    print("=" * 60)
    print(f"FILE {path}  bytes={len(b)} lines={len(lines)} CRLF={b.count(chr(13).encode())if False else b.count(b(chr(13)) if False else b'\r')} LF={b.count(b'\n')}")
    for pat in patterns:
        rx = re.compile(pat)
        for i, ln in enumerate(lines, 1):
            if rx.search(ln):
                s = ln.strip()
                if tail and len(s) > tail:
                    s = "..." + s[-tail:]
                print(f"  L{i}: {s}")

probe("SKILL.md", [r"AUTO_EVOLVE_START", r"AUTO_EVOLVE_END", r"已析出的可编辑项", r"^- P9[0-9]"], tail=600)
probe("CORE.md", [r"^## 总纲", r"可编辑者", r"分工说明", r"来源映射", r"命题库现", r"纲要共", r"C1–C", r"心律"], tail=400)
probe("core/part-01.md", [r"C4 索引", r"可编辑项", r"^- \*\*C9[0-9]", r"^- \*\*C8[0-9]"], tail=500)
probe("core/part-04.md", [r"^# ", r"^## ", r"^- \*\*C9[0-9]"], tail=500)
