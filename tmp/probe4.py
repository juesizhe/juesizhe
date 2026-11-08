# -*- coding: utf-8 -*-
import os
BASE = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
sk = open(os.path.join(BASE, "SKILL.md"), 'rb').read().decode('utf-8').split('\n')
print("=== SKILL.md L222–L233 全文（P96 条目体例） ===")
for i in range(222, 234):
    print(f"--L{i}--")
    print(sk[i - 1])
print()
p4 = open(os.path.join(BASE, "core/part-04.md"), 'rb').read().decode('utf-8').split('\n')
print("=== part-04.md C95 条目（末条体例） ===")
for i, ln in enumerate(p4, 1):
    if ln.strip().startswith("- **C95"):
        for j in range(i, min(i + 3, len(p4) + 1)):
            print(f"--L{j}--")
            print(p4[j - 1])
        break
