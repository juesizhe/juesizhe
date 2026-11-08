# -*- coding: utf-8 -*-
"""落库块 B：core/part-04.md（C96 条目） + core/part-01.md（C4 索引计数与清单）"""
import os
BASE = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"
EOL = "\r\n"

# ================= part-04.md：追加 C96 条目 =================
P4 = os.path.join(BASE, "core", "part-04.md")
raw = open(P4, 'rb').read()
assert raw.count(b'\r') == raw.count(b'\r\n'), "part-04 裸 CR 存在"
txt = raw.decode('utf-8')
lines = txt.split(EOL)
n0 = len(lines)

# 去掉尾部冗余空行，保留以非空行结尾
while lines and lines[-1].strip() == "":
    lines.pop()
tail_empty_orig = txt.endswith(EOL + EOL)
print("part-04 原始行数", n0, "| 去空行后", len(lines), "| 原以空行结尾:", tail_empty_orig)

C96 = ("- **C96 讥与默：一句讥评落下后这笔「被如此评断」之记账方位 × 这一科目之指派者与可反问性 × 不回应（默）记入哪个科目**（← P97）："
       "讥不是「说重了一句话」而是**挂上一笔账**；判准不在「讥得多重／伤得深不深／忍了多久／回不回嘴」（量），"
       "也不在「讥嘲 vs 直谏」这一领域划分——中华一侧四家判词互反而各留其位：《孟子·离娄下》「言人之不善，当如后患何？」、"
       "《论语·阳货》「道听而涂说，德之弃也」、《庄子·齐物论》「大道不称，大辩不言」、《维摩诘所说经·入不二法门品》文殊问不二法门而维摩诘默然无言——"
       "而在三件可分别移动的事：**①这笔「被如此评断」记在哪一本账下**——Eisenberger、Lieberman 与 Williams *Science* 2003;302(5643):290–292"
       "（DOI 10.1126/science.1089134）示社会排斥时前扣带回活动升高且与自陈苦恼正相关，Kross 等 *PNAS* 2011;108(15):6270–6275"
       "（DOI 10.1073/pnas.1102693108）示社会拒斥与物理痛共享躯体感觉表征，故讥评在外部读数上近乎零事件（无接触、无伤痕）而账已落在身体里："
       "账不在「伤之量」上而在「挂在谁名下」上；迈蒙尼德《密西拿·托拉·品德法》7:4 续出「恶言杀说者、听者与被说者三者，而听者甚于说者」，"
       "即这笔账同时开在讥者与在场者名下；**②这一科目由谁开、这开法可否被反问**——阿奎那《神学大全》IIa-IIae q.75 a.1 以讥嘲（derisio）"
       "之别于辱骂、诽谤、搬弄在其**意在使对方羞**而非夺其荣誉或坏其名声，科目之开立由讥者之意图定；亚里士多德《尼各马可伦理学》IV.8（1128a）"
       "给出可反问之把手：中道者以「不使取笑对象痛苦」为约束，讥嘲者「不惜一切求笑」，同一句玩笑之判词随「能不能拿这句话去问讥者一句」而改；"
       "**③不回应（默）记入哪个科目**——Williams、Cheung 与 Choi *JPSP* 2000;79(5):748–762（DOI 10.1037/0022-3514.79.5.748）示被无视者"
       "归属、控制、自尊与存在意义四需受损且随后更易从众，迈蒙尼德《品德法》7:5–7:6 已把「别说某某，我不想说发生了什么」这类**不说**判为"
       "「恶言之尘」、以玩笑口吻出之者仍算，故默不是零账而是另一本账。**可观察之量**：被讥者四需读数与反刍时长（①维）、"
       "讥评之可反问性与讥者回应率（②维）、沉默条件下之四需亏损与从众率（③维）；**失效表现**：账仍开在被讥者名下而讥者与听者名下不记、"
       "讥评不容反问而与可反问时无别、沉默与被讥评在四需上同科。**心律**：「没人说了」≠「账销了」，「回了一句嘴」≠「记在他名下那笔动了」，"
       "「大家都笑了」≠「这笔账只挂在被讥者名下」。**分界**：与 **C93 名与主**之别在「位 vs 分」（名给出位置，讥给出分数），"
       "与 **C92 羞与立**之别在「自感 vs 对人」（羞记在自家账上，讥由他人挂上），与 **C95 怨与直**之别在「讨 vs 挂」"
       "（怨是我要讨之账，讥是别人挂在我名下之账）；安萨里《圣学复苏》第三卷第四章「论舌之祸」列讥嘲取笑为二十过之第十一而主张沉默之德，"
       "迈蒙尼德则以不说亦属恶言之尘，二者为真矛盾，保留而不调和。**可商榷**：若把这笔「被如此评断」之记账方位由被讥者名下移置讥者名下"
       "而被讥者之苦恼读数与四需亏损一无所变，则第一维落空；若讥评之科目完全不可被反问与可被反问时相比被讥者之反刍时长与从众倾向无差别，"
       "则第二维落空；若令讥者彻底沉默（不讥亦不评）时被讥者之四需读数与被公开讥评者无差别，则第三维落空。")
print("C96 条目字符数：", len(C96))
assert len(C96) <= 2000, "条目超 2000 字符"

lines.append(C96)
lines.append("")          # 结尾空行（与 EOL 拼接后文件以 CRLF 收尾）
open(P4, 'wb').write(EOL.join(lines).encode('utf-8'))
nb = open(P4, 'rb').read()
print("part-04 写入后", len(nb), "字节；裸 CR =", nb.count(b'\r') - nb.count(b'\r\n'),
      "| C96 命中:", nb.decode('utf-8').count("**C96 讥与默"))

# ================= part-01.md：C4 索引计数与清单 =================
P1 = os.path.join(BASE, "core", "part-01.md")
raw1 = open(P1, 'rb').read()
assert raw1.count(b'\r') == raw1.count(b'\r\n'), "part-01 裸 CR 存在"
lines1 = raw1.decode('utf-8').split(EOL)
n1 = len(lines1)

cnt = 0
for i, ln in enumerate(lines1):
    if "可编辑项八十九类" in ln:
        lines1[i] = ln.replace("可编辑项八十九类", "可编辑项九十类")
        cnt += 1
assert cnt == 1, f"part-01 计数命中 {cnt} 处"

anchor = "反刍之记账科目（C95）。"
addition = "90一句讥评落下后这笔「被如此评断」之记账方位（被讥者名下／讥者名下／听者与共同体之册）、这一科目之指派者与可反问性、不回应（默）记入哪个科目（C96）。"
cnt2 = 0
for i, ln in enumerate(lines1):
    if anchor in ln and "（C96）" not in ln:
        lines1[i] = ln.replace(anchor, anchor + addition)
        cnt2 += 1
assert cnt2 == 1, f"part-01 清单命中 {cnt2} 处"

open(P1, 'wb').write(EOL.join(lines1).encode('utf-8'))
nb1 = open(P1, 'rb').read()
print("part-01 写入后", len(nb1), "字节；行数", len(lines1), "（原", n1, "）；裸 CR =", nb1.count(b'\r') - nb1.count(b'\r\n'))
t1 = nb1.decode('utf-8')
print("part-01 九十类:", t1.count("可编辑项九十类"), "| 第 90 项:", t1.count("（C96）"))
