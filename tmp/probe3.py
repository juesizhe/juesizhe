# -*- coding: utf-8 -*-
import re, os
BASE = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
p = os.path.join(BASE, "CORE.md")
lines = open(p, 'rb').read().decode('utf-8').split('\n')
for i in list(range(60, 66)):
    s = lines[i - 1].strip()
    print(f"[CORE L{i}] {s[-500:]}")
    print()
print("=== 全文件 grep 95 项/八十九 ===")
for i, ln in enumerate(lines, 1):
    if re.search(r"八十九|95 项|共 95|95 类", ln):
        print(f"  L{i}: ...{ln.strip()[-260:]}")
print()
print("=== part-04.md 行尾空检测 ===")
b = open(os.path.join(BASE, "core/part-04.md"), 'rb').read()
print("bytes", len(b), "CRLF", b.count(b'\r\n'), "LF", b.count(b'\n'), "endswith CRLF", b.endswith(b'\r\n'))
print("tail repr:", repr(b[-200:]))
print()
print("=== SKILL.md / CORE.md / part-01.md EOL ===")
for f in ["SKILL.md", "CORE.md", "core/part-01.md", "PHILOSOPHY.md", "references/tuiyan_pool_state.md", "references/evidence_ledger.md"]:
    bb = open(os.path.join(BASE, f), 'rb').read()
    print(f"{f}: bytes={len(bb)} CRLF={bb.count(b'\r\n')} LF={bb.count(b'\n')} bareCR={bb.count(b'\r')-bb.count(b'\r\n')} endCRLF={bb.endswith(b'\r\n')}")
