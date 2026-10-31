# -*- coding: utf-8 -*-
"""2026-10-26 23:05 夜间汇总精炼（第十五次 · 轻量模式）· PHILOSOPHY.md 蒸馏日志落痕
插入位置：蒸馏日志区末尾（第 809 行，即「## 素材储备」之前的空行处）。
纪律：二进制读写；EOL.join 拼接（防行尾污染）；assert 定位唯一；落盘前核裸 LF=0。
"""
import os, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHIL = os.path.join(ROOT, "PHILOSOPHY.md")
CORE = os.path.join(ROOT, "CORE.md")
EOL = "\r\n"

raw = open(PHIL, "rb").read().decode("utf-8")
lines = raw.split(EOL)
orig = list(lines)

# 定位插入点： 「## 素材储备」 之前的空行
heads = [i for i in range(len(lines)) if lines[i].startswith("## 素材储备")]
assert len(heads) == 1, f"素材储备 定位数 {len(heads)}"
ins = heads[0] - 1
assert lines[ins].strip() == "", f"插入点非空: {lines[ins]!r}"

core_b = os.path.getsize(CORE)
core_kb = core_b / 1024

HEAD = "### 2026-10-26 | 夜间汇总精炼（第十五次执行 · **轻量模式** · 覆盖当日 P81–P82 共 2 条新增）"
BODY = [
    "- **门槛判定**：当日新增 **2 条**——**P81** 出自 00:00 夜间批处理（T078 多重宇宙与缘起，云端 Hy4 Preview 承担全部环节），"
    "**P82** 出自 10:00 白天批处理（T079 熵与秩序，本机 ollama qwen3:14b 承担核心哲思推理，落库改称「序与散」）。"
    "2 条 ∈ [1,2] → 取**轻量模式**；且今日为周一，按 `references/budget.md` 第三节硬规则 1「`CORE.md` 整份重写默认改为每周六一次」，"
    "**本轮不整份重写 `CORE.md`**。",
    "- **五查（开场即跑 `scripts/check_core_domains.py`）**：①来源映射 81 行齐全且最大 Cn＝81＝纲要最大 Cn，抬头双计数同为 81；"
    "②条目物理域与域标题声明**零错位**；③无误置条目；④七域分工说明行**全部齐备**（含 2026-10-25 第十四次补出的「修持 · 转化域」整行）；"
    "⑤抬头计数自洽。**四处计数经查已同值于「七十五类」**（SKILL.md P4 ／ CORE 总纲 ／ C4 索引 ／ 分工说明末项），"
    "按 2026-10-22 教训**不为凑改动而改数**，故本轮 SKILL.md **零改动**。",
    "- **合并 0 / 删除 0**：独立复核四组疑似同构，沿用 **P34 × P6 判例**（具体化 / 换轨 / 投影 ≠ 冗余）**全部裁定不合**，改以对举登记——"
    "①**C80 × C72**：C72 判一次**解释**的界外残留被记为「无关」还是「未知」（记账科目），"
    "C80 判**未获签发者是否仍留有一个可读回、可再入结算的格位**（位置是否保留）；"
    "证据群零重叠（Freivogel 2011／Elitzur 与 Vaidman 1993＋Kwiat 1995 vs Rozenblit 与 Keil 2002、珀尔与麦肯齐 2018）。"
    "②**C80 × C53**：同用「签发」一词而对象不同——C53 判**成员资格**由谁签发、尺规能否由被判者改写，C80 判**这一个世界**由谁签给「我在此」。"
    "③**C81 × C72**：同问「这条界由谁划」，而 C72 对象为**解释**（在哪里停、可否被反问），"
    "C81 对象为**物理过程**（界外移一格是否改判、排放承接者是谁、换尺后能否原样回读），第②③维为 C72 所无；"
    "证据群零重叠（England 2013／2015、Penrose 2010、Prigogine 1977 vs Rozenblit 与 Keil 2002、珀尔与麦肯齐 2018）。"
    "④**C81 × C73**：C73 第③维判换模型之**迁移义务落在谁身上**（义务归属），C81 第③维判换尺后**判据能否被原样回读**（可读性），二者可分别失效。",
    "- **措辞精炼（本轮实质改动，共 8 行）**："
    "(1) **无损清理**：移除 16 条纲要条目标题中的**落库流水元信息**（日期／场次／模型／编排者分工），统一收敛为「（← Pn）」，省 **805 字符**；"
    "该流水在 `PHILOSOPHY.md` 推演日志与采纳记录中均已留痕，故无信息损失。副产物：`prompts/core_index.md` 同步缩小，每场推演固定输入随之下降。"
    "(2) **六条最长条目之「与既有命题的关系」段定向压缩**，省 **765 字符**："
    "C35 607→300、C38 479→300、C32 380→290、C36 384→280、C28 325→270、C29 307→275。"
    "保留全部被引 C 编号、分工／差别之判语、「证据群零重叠」与「不合并」结论，只删展开性赘述；"
    "**判准句、三维度、可观察之量、失效表现、本条之骨（证据群）、名实先行、反直觉、点化、可证伪 一字未动**。"
    "(3) **补体例**：C81 原缺「与既有命题的关系／为 C4 补出第七十五项／点化／可证伪」四段，本轮补齐"
    "（可证伪三句与该条三维度之可观察之量、失效表现一一对应）；C80、C81 之新对举并入正文。",
    "- **体量（本轮未解决，如实记为待裁定）**：`CORE.md` 310,491B → **%d B（%.1fKB／预算 300KB，%d%%）**，G-BUDGET 仍为 **! 超预算**。"
    "轻量模式下可安全取得的净压缩仅 **−1.5KB**——流水清理 805 字符被新增对举（+241／+540）与体例补齐抵消过半。"
    "**实测结论：以「措辞精炼」无法解决体量**——81 条条目正文合计约 101,400 字符，占全文 82%%；要降到 250KB 须删减约 17%% 的条目正文，"
    "属**完整模式**职权，不在轻量模式范围内。"
    "**建议推迟至 2026-10-31（周六）完整模式一次性处理**，两条候选路径："
    "①**裁并** C1–C40 中 7 条 >2500 字符的长条目（C35 2910／C38 2819／C28 2721／C32 2579／C36 2554／C29 2582／C37 2557）；"
    "②**分册**（`CORE.md` 留七区 + C1–C40，C41–C81 另立一册）——但分册须同步改 `build_deduce.py`／`preflight.py`／`check_core_domains.py` "
    "三处对 `CORE.md` 的硬编码路径，并须在 `SKILL.md` 工作流章增写分册说明，"
    "而「只动 `AUTO_EVOLVE` 标记内条目与 `CORE.md`、绝不改写 SKILL 其他章节」是铁律，**故分册必须先经用户裁定放行**。"
    "另：`PHILOSOPHY_SUMMARY.md` G-SUM 已达 5162／5200（99%%），下一轮压缩前亦须先行处理。"
    % (core_b, core_kb, round(core_kb / 300 * 100)),
    "- **新条目字数上限（本轮起执行）**：落库条目一律 **≤2000 字符**（C81 落库 1582 字符，已达标）。按此速率每增一条约 +6KB。",
    "- **红线遵守**：本次**未**读取、未并入 `references/tuiyan_corpus.md`（草稿素材池）与 `references/tuiyan_pool_state.md`（消费台账），"
    "素材池草稿无一被升级为命题或写入 `CORE.md`。**`SKILL.md` 本轮零改动**（四处计数已自洽，未为凑改动而改数）。"
    "`CORE.md` 改动 8 行，全部落在条目区与对举补写；七区（总纲／C4 索引／域标题／分工说明／心律段／来源映射）**未被改动**。"
    "无宗教自称、无涉政、无超自然断言，边界声明五条无误。",
]

new = [HEAD, ""] + [b + "" for b in BODY[:1]]
block = [HEAD, ""]
for b in BODY:
    block.append(b)
    block.append("")
# 去掉末尾多余空行，保留一个
while block and block[-1] == "":
    block.pop()
block.append("")

lines[ins:ins] = block

out = EOL.join(lines)
crlf = out.count("\r\n")
bare_lf = out.count("\n") - crlf
bare_cr = out.count("\r") - crlf
print(f"[EOL] CRLF={crlf} 裸LF={bare_lf} 裸CR={bare_cr}  （落盘前裸 LF 必须为 0）")
assert bare_lf == 0 and bare_cr == 0, "存在裸 LF / 裸 CR，拒绝写盘"
open(PHIL, "wb").write(out.encode("utf-8"))

sm = difflib.SequenceMatcher(None, orig, lines, autojunk=False)
prev = 0
n = 0
for b in sm.get_matching_blocks():
    if b.a > prev:
        n += 1
        for k in range(prev, b.a):
            print(f"  [+] 行 {k+1}: {lines[k][:60]}")
    prev = b.a + b.size
print(f"[DIFF] 新增 {n} 行（分段 {len([x for x in lines[ins:ins+len(block)] if x.strip()])} 段）")
# 核验段数
segs = [x for x in lines[ins:ins + len(block)] if x.strip()]
print(f"[核验] 落痕段数 = {len(segs)}（预期 8 段：标题 + 7 条要点）")
assert len(segs) == 8, f"落痕段数异常 {len(segs)}"
print(f"[OK] PHILOSOPHY.md {os.path.getsize(PHIL)/1024:.1f}KB")
