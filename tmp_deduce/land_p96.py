# -*- coding: utf-8 -*-
"""P96 怨与直 / C95 落库脚本（按文件分块，幂等，可单独重跑）。"""
import os
import sys

BASE = "C:/Users/Administrator/.workbuddy/skills/philosopher-sage"

P96_LINES = [
    "- P96 怨与直（可商榷）：怨之结算的判准，不在「怨得多深／该不该怨／忍了多久／报得对不对等」（量），也不在「以直报怨 vs 报怨以德」这一领域划分，而在「这一份不平记在哪一本账下（受怨者名下／施为者名下／共同体之册）× 销账通道由谁开、这开法可否被反问 × 罚出之后这笔账是否停手、反刍记入哪个科目」。",
    "  ①科学：de Quervain 等 *Science* 2004;305(5688):1254–1258（DOI 10.1126/science.1100735）——有效惩罚（相对于象征性惩罚）激活背侧纹状体，激活越强者愿付越大代价；Carlsmith、Wilson 与 Gilbert *JPSP* 2008;95(6):1316–1324（DOI 10.1037/a0012165）——施加惩罚者事后反刍更多、感受更差，而人事先预判相反。",
    "  ②三教与诸子：儒《论语·宪问》「以直报怨，以德报德」；道《老子》六十三章「报怨以德」；佛《法句经·双品》「于此世界中，非以怨止怨，唯以慈止怨」；《礼记·表记》「报者，天下之利也」「以怨报怨，则民有所惩」。",
    "  ③犹太：迈蒙尼德《密西拿·托拉·悔改法》2:9——人对人之过犯非归还所欠并求得对方原谅不得赦，三次请托后可止步，**不肯宽恕者反成罪人**。",
    "  ④希腊：亚里士多德《修辞学》II.9（1386b8–20）——义愤（nemesan）是为他人不应得之好运而痛，为怜悯之对待面；若痛因怕自己受损，则已是恐惧而非义愤。",
    "  ⑤伊斯兰：安萨里《圣学复苏》论怒、怨恨与嫉妒之害（第三卷第五章，Kitāb āfāt al-ghaḍab wa-l-ḥiqd wa-l-ḥasad）。",
    "  ⑥思潮：阿伦特《人的境况》1958 第 33 节——无人能宽恕自己，宽恕与承诺皆依赖复数性。",
    "  推演新知：怨不是「未报之债」而是「已挂未结之账」；罚得落地不等于账结得掉——销账与否取决于这笔账开在谁名下、通道由谁开、结后有无停手之把手。",
    "  可证伪：①把怨之记账方位由受怨者名下移置共同体之册，而反刍时长与报复意愿一无所变，则第①维落空；②增设归还与三分请托式求恕通道，而销账率与未设时相同，则第②维落空；③令惩罚完全无法落地，而施加者事后反刍与惩罚落地者无差别，则第③维落空。",
    "  与既有命题的关系：**P13 报（C12，判时历）在「报未行时」的前置补出**——C12 判这一报之后关系是否仍留更新入口，本条判这一报尚未作出而怨已挂账时这笔账开在谁名下；与 P95 债与偿（C94）之分界为「取 vs 怨」（债起于转移，怨起于处置），与 P93 羞与立（C92）之分界为「自感 vs 对人」（羞记在自家账上，怨指向他人或共同体）。",
    "  可编辑项新增第 89：一份不平被挂起时这笔「不平」之记账方位（受怨者名下／施为者名下／共同体之册）× 销账通道之开启者与可反问性 × **罚出之后这笔账是否停手与反刍之记账科目**（← P96）。",
    "  预算｜输入：约 14,000 ｜ WebSearch：6 ｜ 本地推理：0 ｜ 采纳：P96",
]

C95_BODY = (
    "- **C95 怨与直：一份不平之记账方位 × 销账通道之开启者与可反问性 × 罚出之后这笔账是否停手与反刍之记账科目**（← P96）："
    "怨不是尚未报出之债，而是**已经挂起、尚未结清之账**；判准不在「怨得多深／该不该怨／忍了多久／报得对不对等」（量），"
    "也不在「以直报怨 vs 报怨以德」这一领域划分——中华一侧三家判词互反而各留其位：《论语·宪问》「以直报怨，以德报德」、《老子》六十三章「报怨以德」、"
    "《法句经·双品》「非以怨止怨，唯以慈止怨」、《礼记·表记》「报者，天下之利也」——而在三件可分别移动的事："
    "**①这笔不平记在哪一本账下**——亚里士多德《修辞学》II.9（1386b8–20）以义愤（nemesan）为怜悯之对待面：为他人不应得之好运而痛方为义愤，"
    "若痛因怕自己受损则已是恐惧而非义愤，故怨之正当性挂在「应得」与「为谁而痛」上，而非挂在受损之量上；"
    "**②销账通道由谁开、这开法可否被反问**——迈蒙尼德《密西拿·托拉·悔改法》2:9 定：人对人之过犯非归还所欠并求得对方原谅不得赦，三次请托后可止步，"
    "而**不肯宽恕者反成罪人**，即销账权在受怨者手里、且拒不销账会把自家转成欠账人；阿伦特《人的境况》1958 第 33 节续出：无人能宽恕自己，"
    "宽恕与承诺皆依赖复数性，故销账通道只能在共在场开，不能自家开；**③罚出之后这笔账是否停手、反刍记入哪个科目**——"
    "de Quervain 等 *Science* 2004;305(5688):1254–1258 示：有效惩罚（相对于象征性惩罚）激活背侧纹状体，激活越强者愿付越大代价；"
    "Carlsmith、Wilson 与 Gilbert *JPSP* 2008;95(6):1316–1324 示：施加惩罚者事后反刍更多、感受更差，而人事先预判相反。"
    "**心律**：「罚得痛快」≠「账销得掉」，「忍得下」≠「账记在他名下」，「求得原谅」≠「对方开了口子」。"
    "**可商榷**：若把怨之记账方位由受怨者名下移置共同体之册而反刍时长与报复意愿一无所变，则第一维落空；"
    "若增设归还与三分请托式求恕通道而销账率与未设时相同，则第二维落空；若令惩罚完全无法落地而施加者事后反刍与惩罚落地者无差别，则第三维落空。"
)

ADD_P4 = "89一份不平被挂起时这笔「不平」之记账方位（受怨者名下／施为者名下／共同体之册）、销账通道之开启者与可反问性、罚出之后这笔账是否停手与反刍之记账科目（P96）。"
ADD_C4 = "89一份不平被挂起时这笔「不平」之记账方位（受怨者名下／施为者名下／共同体之册）、销账通道之开启者与可反问性、罚出之后这笔账是否停手与反刍之记账科目（C95）。"
ADD_XIN = (
    "；而今日再增之一问（C95）则续出——**「罚得痛快」不等于「账销得掉」，「忍得下」不等于「账记在他名下」，"
    "「求得原谅」不等于「对方开了口子」**：一份不平被挂起时这笔不平记在哪本账下、销账通道由谁开且可否被反问、"
    "罚出之后这笔账是否停手而反刍记入哪个科目，才是三件可以分别移动的事（C95）"
)


def readf(p):
    b = open(p, "rb").read()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n")
    eol = "\r\n" if (crlf and crlf == lf) else "\n"
    return b.decode("utf-8"), eol


def writef(p, text, eol):
    lines = text.split("\n")
    data = eol.join(lines).encode("utf-8")
    open(p, "wb").write(data)


def idx_exact(lines, startswith):
    hits = [i for i, l in enumerate(lines) if l.startswith(startswith)]
    assert len(hits) == 1, (startswith, len(hits))
    return hits[0]


def block_skill():
    p = os.path.join(BASE, "SKILL.md")
    t, eol = readf(p)
    if "- P96 " in t:
        print("  SKILL 已写入，跳过")
        return
    lines = t.split("\n")
    i = idx_exact(lines, "- P4 自由")
    assert lines[i].count("可编辑项八十八类") == 1
    lines[i] = lines[i].replace("可编辑项八十八类", "可编辑项八十九类")
    lines[i] = lines[i] + ADD_P4
    assert lines[i].rstrip().endswith("（P96）。")
    ie = idx_exact(lines, "<!-- AUTO_EVOLVE_END -->")
    assert not any("\n" in x for x in P96_LINES)
    lines[ie:ie] = P96_LINES
    writef(p, "\n".join(lines), eol)
    print("  SKILL.md 写入完成（+{} 行）".format(len(P96_LINES)))


def block_core():
    p = os.path.join(BASE, "CORE.md")
    t, eol = readf(p)
    if "- C95 ← P96" in t:
        print("  CORE 已写入，跳过")
        return
    lines = t.split("\n")
    # 1 总纲：可编辑者八十八 → 八十九 + 心律段追加 C95
    i9 = idx_exact(lines, "世界是关系的暂稳态")
    assert lines[i9].count("可编辑者八十八") == 1
    lines[i9] = lines[i9].replace("可编辑者八十八", "可编辑者八十九")
    assert lines[i9].rstrip().endswith("（C94）")
    lines[i9] = lines[i9] + ADD_XIN
    # 2 分工说明末项
    i39 = idx_exact(lines, "- 上述 C7")
    assert lines[i39].count("/ C94 共八十七项") == 1
    assert lines[i39].count("可编辑项八十八类") == 1
    lines[i39] = lines[i39].replace("/ C94 共八十七项", "/ C94 / C95 共八十八项")
    lines[i39] = lines[i39].replace("可编辑项八十八类", "可编辑项八十九类")
    # 3 分册导航表 与 分工说明域行：域清单追加 C95
    i26 = idx_exact(lines, "| 4 | 关系 · 公共域 |")
    assert lines[i26].count("C91、C94 |") == 1
    lines[i26] = lines[i26].replace("C91、C94 |", "C91、C94、C95 |")
    i35 = idx_exact(lines, "- **关系 · 公共域 C9–C13")
    assert lines[i35].count("C91、C94**：") == 1
    lines[i35] = lines[i35].replace("C91、C94**：", "C91、C94、C95**：")
    # 4 来源映射抬头
    i67 = idx_exact(lines, "> 命题库现 ")
    assert lines[i67].count("**94 条**") == 1 and lines[i67].count("P11–P95") == 1
    lines[i67] = lines[i67].replace("**94 条**", "**95 条**").replace("P11–P95", "P11–P96")
    i68 = idx_exact(lines, "> 纲要共 ")
    assert lines[i68].count("**94 条**") == 1 and lines[i68].count("C1–C94") == 1
    lines[i68] = lines[i68].replace("**94 条**", "**95 条**").replace("C1–C94", "C1–C95")
    # 5 映射行
    i163 = idx_exact(lines, "- C94 ← P95")
    lines.insert(i163 + 1, "- C95 ← P96")
    writef(p, "\n".join(lines), eol)
    print("  CORE.md 写入完成（计数四处 + 域清单两处 + 映射抬头 + 映射行）")


def block_part01():
    p = os.path.join(BASE, "core/part-01.md")
    t, eol = readf(p)
    if "（C95）。" in t:
        print("  part-01 已写入，跳过")
        return
    lines = t.split("\n")
    i = idx_exact(lines, "- **C4 自由 = 可觉知地编辑**")
    assert lines[i].count("可编辑项八十八类") == 1
    lines[i] = lines[i].replace("可编辑项八十八类", "可编辑项八十九类")
    assert lines[i].rstrip().endswith("（C94）。")
    lines[i] = lines[i] + ADD_C4
    writef(p, "\n".join(lines), eol)
    print("  part-01.md 写入完成（C4 索引计数 + 清单第 89 项）")


def block_part04():
    p = os.path.join(BASE, "core/part-04.md")
    t, eol = readf(p)
    if "- **C95 怨与直" in t:
        print("  part-04 已写入，跳过")
        return
    lines = t.split("\n")
    i5 = idx_exact(lines, "### 关系 · 公共域")
    assert lines[i5].count("C91、C94）") == 1
    lines[i5] = lines[i5].replace("C91、C94）", "C91、C94、C95）")
    i94 = idx_exact(lines, "- **C94 债与偿")
    assert not any("\n" in x for x in [C95_BODY])
    assert len(C95_BODY) <= 2000, len(C95_BODY)
    lines.insert(i94 + 1, C95_BODY)
    writef(p, "\n".join(lines), eol)
    print("  part-04.md 写入完成（C95 条目 {} 字符）".format(len(C95_BODY)))


BLOCKS = {
    "skill": block_skill,
    "core": block_core,
    "part01": block_part01,
    "part04": block_part04,
}

if __name__ == "__main__":
    which = sys.argv[1:] or list(BLOCKS)
    for k in which:
        BLOCKS[k]()
    print("完成：", ", ".join(which))
