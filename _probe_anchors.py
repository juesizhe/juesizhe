import os

SKILL = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"

def show(path, label, lines):
    # lines: list of 1-indexed line numbers to print, with +/- context
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    eol_crlf = raw.count(b"\r\n")
    eol_lf = raw.count(b"\n") - eol_crlf
    parts = text.split("\n")
    total = len(parts)  # number of lines (trailing newline -> last empty)
    print("="*70)
    print(f"FILE: {label}  ({path})")
    print(f"  total split-lines={total}  CRLF={eol_crlf}  bare-LF={eol_lf}")
    print("-"*70)
    for ln in lines:
        if 1 <= ln <= total:
            print(f"[{ln}] {parts[ln-1]}")
    print()

# SKILL.md anchors
show(os.path.join(SKILL,"SKILL.md"), "SKILL.md",
     [80,81,82,83,84, 276,277,278,279,280,281,282,283,284])

# CORE.md anchors
show(os.path.join(SKILL,"CORE.md"), "CORE.md",
     [9,10, 26,27, 39,40, 166,167,168])

# part-01.md anchors
show(os.path.join(SKILL,"core","part-01.md"), "part-01.md",
     [8,9,10,11,12])

# part-04.md anchors
show(os.path.join(SKILL,"core","part-04.md"), "part-04.md",
     [4,5,6, 42,43,44,45,46])
