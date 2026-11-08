# -*- coding: utf-8 -*-
"""落库块 C：CORE.md —— 总纲心律 / 导航表 / 分工说明域行与末项 / 来源映射三处抬头 + 映射行"""
import os
BASE = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
P = os.path.join(BASE, "CORE.md")
EOL = "\r\n"
SIZE_PART04 = os.path.getsize(os.path.join(BASE, "core", "part-04.md"))
KB = round(SIZE_PART04 / 1024)

raw = open(P, 'rb').read()
assert raw.count(b'\r') == raw.count(b'\r\n'), "CORE 裸 CR 存在"
lines = raw.decode('utf-8').split(EOL)
n0 = len(lines)

def rep(old, new, expect=1, where=None):
    cnt = 0
    for i, ln in enumerate(lines):
        if where and not where(ln):
            continue
        if old in ln:
            lines[i] = ln.replace(old, new)
            cnt += 1
    assert cnt == expect, f"[{old[:24]}] 命中 {cnt} 处，期望 {expect}"
    return cnt

# ---- 原地 replace（全部用原始下标，最后再 insert）----
rep("可编辑者八十九", "可编辑者九十")                            # L9 总纲计数
rep("| `core/part-04.md` | 99KB |", f"| `core/part-04.md` | {KB}KB |")  # L26 导航表体量
rep("C91、C94、C95 | `core/part-04.md`", "C91、C94、C95、C96 | `core/part-04.md`")  # L26 区间
rep("C49–C57、C60、C62、C64、C67、C71、C74、C76、C78、C91、C94、C95**：",
    "C49–C57、C60、C62、C64、C67、C71、C74、C76、C78、C91、C94、C95、C96**：")       # L35 域行抬头
rep("/ C94 / C95 共八十八项", "/ C94 / C95 / C96 共八十九项")      # L39 末项
rep("构成**可编辑项八十九类**。", "构成**可编辑项九十类**。")     # L39 末项
rep("> 命题库现 **95 条**：P0、P1、P2、P4–P9、P11–P96", "> 命题库现 **96 条**：P0、P1、P2、P4–P9、P11–P97")  # L67
rep("> 纲要共 **95 条**（C1–C95", "> 纲要共 **96 条**（C1–C96")     # L68

# ---- 行尾追加 1：L9 总纲心律段续出 C96 ----
anchor9 = "才是三件可以分别移动的事（C95）"
add9 = ("；而今日再增之一问（C96）则续出——**「没人说了」不等于「账销了」，「回了一句嘴」不等于"
        "「记在他名下那笔动了」，「大家都笑了」不等于「这笔账只挂在被讥者名下」**："
        "一句讥评落下后这笔「被如此评断」记在哪本账下、这一科目由谁开且可否被反问、"
        "不回应（默）记入哪个科目，才是三件可以分别移动的事（C96）")
cnt9 = 0
for i, ln in enumerate(lines):
    if anchor9 in ln and "（C96）" not in ln:
        lines[i] = ln.replace(anchor9, anchor9 + add9)
        cnt9 += 1
assert cnt9 == 1, f"总纲心律命中 {cnt9} 处"

# ---- 行尾追加 2：L35 分工说明域行补 C95 与 C96 描述 ----
anchor35 = "本条判一段东西已经过手而尚未偿清时这笔「已取未偿」挂在谁名下，分界为「许 vs 取」）；"
add35 = ("**C95 怨与直**，判「一份不平被挂起时这笔不平挂在谁名下、销账通道由谁开且可否被反问、"
         "罚出之后这笔账是否停手」——是 C94 债与偿在**处置**一侧的补完（C94 判一段东西已过手而未偿清时这笔账挂在谁名下，"
         "C95 判一份不平已挂起而未结算时这笔账挂在谁名下，分界为「取 vs 怨」）；"
         "**C96 讥与默**，判「一句讥评落下后这笔『被如此评断』挂在谁名下、这一科目由谁开且可否被反问、"
         "不回应（默）记入哪个科目」——是 C95 怨与直在**评断**一侧的补完（C95 判我要讨之账，C96 判别人挂在我名下之账，"
         "分界为「讨 vs 挂」；与 C93 名与主之别在「位 vs 分」，与 C92 羞与立之别在「自感 vs 对人」）；")
cnt35 = 0
for i, ln in enumerate(lines):
    if anchor35 in ln and "**C96 讥与默**" not in ln:
        lines[i] = ln.replace(anchor35, anchor35 + add35)
        cnt35 += 1
assert cnt35 == 1, f"域行命中 {cnt35} 处"

# ---- insert：映射行 - C95 ← P96 之后追加 - C96 ← P97 ----
idx = None
for i, ln in enumerate(lines):
    if ln.strip() == "- C95 ← P96":
        idx = i
assert idx is not None, "未找到映射行 C95 ← P96"
lines.insert(idx + 1, "- C96 ← P97")
assert len(lines) == n0 + 1, f"行数不符 {len(lines)} vs {n0 + 1}"

open(P, 'wb').write(EOL.join(lines).encode('utf-8'))
nb = open(P, 'rb').read()
t = nb.decode('utf-8')
print("CORE 写入后", len(nb), "字节；行数", len(lines), "（原", n0, "）；裸 CR =", nb.count(b'\r') - nb.count(b'\r\n'))
for k in ["可编辑者九十", "可编辑项九十类", "共八十九项", "C96 ← P97", "**C96 讥与默**",
          "命题库现 **96 条**", "纲要共 **96 条**", f"{KB}KB"]:
    print(f"  {k}: {t.count(k)}")
