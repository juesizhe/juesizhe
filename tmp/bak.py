# -*- coding: utf-8 -*-
import os, shutil
BASE = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
for f in ["SKILL.md", "CORE.md", "PHILOSOPHY.md", "core/part-01.md", "core/part-04.md",
          "references/tuiyan_pool_state.md", "references/evidence_ledger.md"]:
    src = os.path.join(BASE, f)
    dst = src + ".1102day"
    shutil.copyfile(src, dst)
    print("bak ->", dst, os.path.getsize(dst))
