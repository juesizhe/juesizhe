# -*- coding: utf-8 -*-
"""2026-10-26 23:05 夜间汇总精炼（第十五次 · 轻量模式）· CORE.md 改动脚本
只做三件事：
  A. 无损清理：移除纲要条目标题中的「落库流水元信息」（日期／场次／模型，PHILOSOPHY.md 已留痕）
  B. 补对举：C80 增两则对举（×C72、×C53）
  C. 补体例：C81 补「与既有命题的关系／为 C4 补出／点化／可证伪」（其余各段已有）
纪律：二进制读写；按行索引操作；assert count==1；落盘前核裸 LF=0。
"""
import re, os, sys, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "CORE.md")
EOL = "\r\n"

raw = open(CORE, "rb").read().decode("utf-8")
lines = raw.split(EOL)
orig = list(lines)


def idx_of(prefix, start=0):
    """按行首前缀定位，返回下标列表"""
    return [i for i in range(start, len(lines)) if lines[i].startswith(prefix)]


def rep(i, old, new, tag):
    assert lines[i].count(old) == 1, f"[{tag}] 命中数 != 1: {lines[i].count(old)}"
    lines[i] = lines[i].replace(old, new, 1)


# ---------- A. 移除标题落库流水元信息 ----------
PROV = re.compile(r'（← (P\d+)，(?!含已并入)[^）]*）')
n_a = 0
saved = 0
for i in range(len(lines)):
    if not lines[i].startswith("- **C"):
        continue
    m = PROV.search(lines[i])
    if m:
        old = m.group(0)
        new = f"（← {m.group(1)}）"
        saved += len(old) - len(new)
        rep(i, old, new, "A")
        n_a += 1
print(f"[A] 清理落库流水 {n_a} 处，省 {saved} 字符")

# ---------- B. C80 补对举 ----------
c80 = idx_of("- **C80 ")
assert len(c80) == 1, f"C80 定位数 {len(c80)}"
i80 = c80[0]
B_ANCHOR = "与 **C15／P16**（无知之结构）对举。"
B_ADD = (
    "与 **C72／P73** 划界而不合并——C72 判**解释**之界外残留被记为无关还是未知（记账科目），"
    "本条判**未获签发者是否仍留有一个可读回、可再入结算的格位**（位置是否保留），"
    "证据群零重叠（Freivogel 2011／Elitzur 与 Vaidman 1993＋Kwiat 1995 vs Rozenblit 与 Keil 2002、珀尔与麦肯齐 2018）；"
    "与 **C53／P54** 同用「签发」一词而对象不同——C53 判**成员资格**由谁签发、尺规能否由被判者改写，"
    "本条判**这一个世界**由谁签给「我在此」，故不合。"
)
rep(i80, B_ANCHOR, B_ANCHOR + B_ADD, "B")

# ---------- C. C81 补体例 ----------
c81 = idx_of("- **C81 ")
assert len(c81) == 1, f"C81 定位数 {len(c81)}"
i81 = c81[0]
C_ANCHOR = "**边界留痕**：改称中性机制名目「序与散」，只取机制结论，未对任何国家、政府、制度、机构、学科或厂商作优劣定性，未引任何政策主张。"
C_ADD = (
    "**与既有命题的关系**：与 **C72／P73** 同问「这条界由谁划」而不合并——"
    "C72 判一次**解释**在哪里停、可否被反问、界外残留记为无关还是未知，"
    "本条判**物理过程**之界外移一格是否改判、排放承接者是谁、换尺后能否原样回读，"
    "第②③维为 C72 所无，证据群零重叠（England 2013／2015、Penrose 2010、Prigogine 1977 vs Rozenblit 与 Keil 2002、珀尔与麦肯齐 2018）；"
    "与 **C73／P74** 对举（C73 判换模型之**迁移义务落在谁身上**，本条判换尺后**判据能否被原样回读**——义务归属 ≠ 可读性）；"
    "与 **C27** 分工（C27 判常设规则之翻转门槛，本条判物理过程之序与散）；"
    "与 **C80／P81** 同用「由谁划／由谁签」之手法而异域（C80 在宇宙论之清单与签发者，本条在物理过程之界、账、尺）。"
    "**为 C4 补出第七十五项可编辑项——序与散之界由谁划、排放记在哪本账、读数失效后尺由谁带过去。**"
    "点化：**别问熵高不高——先问：这条界是谁划的，排放记在谁的账上，尺子失灵的时候由谁把它带过去。**"
    "可证伪：若边界外移一格而秩序之读数毫无改判，则第①维落空；若只换排放之承接者而存续与判读仍完全同幅，则第②维落空；若换尺之后无一判据改判，则第③维落空。"
)
rep(i81, C_ANCHOR, C_ANCHOR + C_ADD, "C")

# ---------- 落盘 ----------
out = EOL.join(lines)
crlf = out.count("\r\n")
bare_lf = out.count("\n") - crlf
bare_cr = out.count("\r") - crlf
print(f"[EOL] CRLF={crlf} 裸LF={bare_lf} 裸CR={bare_cr}")
assert bare_lf == 0 and bare_cr == 0, "存在裸 LF / 裸 CR，拒绝写盘"

open(CORE, "wb").write(out.encode("utf-8"))

# ---------- 改动面逐行核验 ----------
sm = difflib.SequenceMatcher(None, orig, lines, autojunk=False)
blocks = [b for b in sm.get_matching_blocks() if b.size > 0]
changed = []
prev = 0
for b in blocks:
    if b.a > prev:
        changed.append((prev + 1, b.a, orig[prev:b.a], lines[prev + (b.b - b.a):b.b]))
    prev = b.a + b.size
print(f"\n[DIFF] 改动块 {len(changed)} 处：")
for s, e, o, n in changed:
    print(f"  行 {s}-{e}  ({len(o[0])} → {len(n[0])} 字符)")
    for oo, nn in zip(o, n):
        if oo != nn:
            # 打印被替换的片段
            for k in range(min(len(oo), len(nn))):
                if oo[k] != nn[k]:
                    print(f"    原 …{oo[max(0,k-30):k+60]}")
                    print(f"    新 …{nn[max(0,k-30):k+60]}")
                    break
print(f"\n[OK] CORE.md {os.path.getsize(CORE)/1024:.1f}KB")
