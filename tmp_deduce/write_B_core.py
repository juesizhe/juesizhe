#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""落库脚本 B：CORE.md + core/part-01.md + core/part-05.md"""
import os, sys

ROOT = r"C:/Users/Administrator/.workbuddy/skills/philosopher-sage"

C97 = (
    "- **C97 疑与信：一份凭据被撤销后这笔「曾信／今疑」之记账方位 × 撤销权之执有者与可反问性 × 疑而未决之记账科目**（← P98）："
    "疑不是信之减少，而是**另一本账**；判准不在「疑得多深／信得多坚／凭据够不够／撤得快不快」（量），"
    "也不在「该信 vs 该疑」这一领域划分——中华一侧四家判词互反而各留其位："
    "荀子《非十二子》「信信，信也；疑疑，亦信也」（杨倞注「意虽不同，皆归于信」）、"
    "《论语·为政》2.18「多闻阙疑」以疑记入「阙」一空位、"
    "《老子》四十九章「信者吾信之，不信者吾亦信之，德信」、"
    "《华严经·贤首品》「断除疑网出爱流」——而在三件可分别移动的事："
    "**①这笔「曾信／今疑」记在哪一本账下**——Johnson 与 Seifert *JEP:LMC* 1994;20(6):1420–1436"
    "（DOI 10.1037/0278-7393.20.6.1420）示：更正之后被试自陈记得该条已假，后续推论仍沿用被撤回之信息，"
    "唯另给一条可承接其因果结构之说明时持续影响方减弱；即**撤下的是凭据，不是账**。"
    "**②撤销权由谁执、可否被反问**——Kim、Ferrin、Cooper 与 Dirks *JAP* 2004;89(1):104–118"
    "（DOI 10.1037/0021-9010.89.1.104）示：同为一次失效，记为能力之失者以致歉修复、记为诚信之失者以否认修复，"
    "事后有罪证者致歉有效、无罪证者否认有效；修复动作不由失效之量定，而由这笔账开在哪个科目定。"
    "**③疑而未决之部记入哪个科目**——塞克斯都《皮浪学说纲要》卷一以「悬搁」为可长留之科目而由之得宁静，"
    "皮尔士《信念的确定》1877 以疑为「待由探究止息」之不安，《薄伽梵歌》4.40 以疑者记入「毁灭」，"
    "阿奎那《神学大全》IIa-IIae q.1 a.4 以信恰在未见处成立，"
    "安萨里《脱离迷误》自陈销疑不由论证之补足而由「投入胸中之一道光」——同一份未决，五种科目，后续结算各异。"
    "**可观察之量**：更正之回灌率与后续推论之沿用率（①）、信任修复率与撤销之可反问性（②）、"
    "科目改记后可援引／可让渡／结算／撤回之变化（③）；"
    "**失效表现**：改挂账下而后续推论一无所变、不容反问与容反问修复率无别、疑由「悬置」改记「作废」而结算一无所变。"
    "**心律**：「凭据撤得下」≠「旧账跟着撤」，「自陈不信了」≠「账换了本」，「疑悬着没答」≠「疑没入账」。"
    "**真矛盾（保留张力，不得调和）**：《薄伽梵歌》4.40 以疑为须断之最坏科目 vs 塞克斯都以悬搁为达宁静之正途；"
    "荀子「疑疑亦信也」以疑为信之另一形态 vs 阿奎那以信在未见处成立；"
    "《老子》「不信者吾亦信之」把不信者仍记入信之账 vs 皮尔士以探究之终点为疑之止息；"
    "安萨里以销疑不由论证之补足 vs Johnson 与 Seifert 以须另给替代因果说明。"
    "**与既有命题的关系**：**C18 信任：判凭据**（← P19）判失效时之降载通道，本条判失效后之挂账位——"
    "分界为「失效时之降载 vs 失效后之挂账」；**C69 信持与修正**（← P70）判一条反例落哪本账，"
    "本条判整条凭据撤下后落哪本账——分界为「一条反例 vs 整条凭据」；与 **C93 名与主**分界为「挂上 vs 撤下」，"
    "与 **C91 诺与账**为「许 vs 凭」，与 **C96 讥与默**为「一句落下 vs 一份撤下」。"
    "**推演新知**：凭据之撤销与账之撤销是两件事；消解疑之把手不在补足论据，"
    "而在改挂账位、开放撤销之反问通道、为未决之部指定科目。"
    "点化：凭据被撤下了，账未必跟着撤——要紧的是这笔「曾信」还挂在谁名下、撤销的钥匙在谁手里、"
    "还没结论的那一块到底记成了悬置、欠款还是作废。"
    "**为 C4 补出第九十一项可编辑项——凭据失效之挂账位（撤销权／可反问性／未决之科目）。**"
    "本条可商榷：四条真矛盾并列保留，只取「三笔账可分别移动」之判准。"
    "**可证伪**：①改挂账下而回灌率、责任归属与后续推论一无所变；"
    "②换撤销者或令撤销不容被反问而修复率与可援引性一无所变；"
    "③把「疑而未决」由「悬置」一律改记为「作废」而此后之可援引、可让渡、结算与撤回一无所变——"
    "任一成立，对应之维落空。"
)
print("C97 长度 =", len(C97), "字符")
assert len(C97) <= 2000, "C97 超 2000 字符，需压缩"
assert "****" not in C97, "出现四连星号"
assert "。****" not in C97, "出现段间星号瑕疵"


def load_eol(path):
    with open(path, "rb") as f:
        b = f.read()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n")
    eol = "\r\n" if (lf > 0 and crlf == lf) else "\n"
    return b.decode("utf-8"), eol


def save(path, lines, eol, note):
    out = eol.join(lines).encode("utf-8")
    assert b"\r\r\n" not in out, "裸 CR 残留: " + path
    with open(path, "wb") as f:
        f.write(out)
    print("OK", os.path.basename(path), note, "eol=%r 行数=%d" % (eol, len(lines)))


# ============ CORE.md ============
p = os.path.join(ROOT, "CORE.md")
t, eol = load_eol(p)
if "C97 ← P98" in t:
    print("SKIP: CORE.md 已含 C97")
else:
    lines = t.split(eol)
    repls = [
        ("**可编辑者九十**", "**可编辑者九十一**"),
        ("命题库现 **96 条**", "命题库现 **97 条**"),
        ("P11–P97（", "P11–P98（"),
        ("纲要共 **96 条**（C1–C96，无缺号", "纲要共 **97 条**（C1–C97，无缺号"),
        ("C89、C93 | `core/part-05.md`", "C89、C93、C97 | `core/part-05.md`"),
        ("/ C96 共八十九项", "/ C96 / C97 共九十项"),
        ("构成**可编辑项九十类**", "构成**可编辑项九十一类**"),
    ]
    for old, new in repls:
        assert t.count(old) == 1, "CORE 锚点不唯一: %r -> %d" % (old, t.count(old))
    for old, new in repls:
        t = t.replace(old, new, 1)

    # 总纲心律段（行首前缀定位）
    lines = t.split(eol)
    zong = [i for i, l in enumerate(lines) if l.startswith("世界是关系的暂稳态")]
    assert len(zong) == 1, "总纲行不唯一"
    lines[zong[0]] += (
        "；而今日再增之一问（C97）则续出——**「凭据撤得下」不等于「旧账跟着撤」，"
        "「自陈不信了」不等于「账换了本」，「疑悬着没答」不等于「疑没入账」**："
        "一份凭据被撤销后这笔「曾信／今疑」记在哪本账下、撤销之权由谁执且可否被反问、"
        "疑而未决之部记入哪个科目，才是三件可以分别移动的事（C97）"
    )

    # 分工说明 认知域行（不以句号收尾，按行首定位后行尾追加）
    ren = [i for i, l in enumerate(lines) if l.startswith("- **认知 · 语言 · 技术域 C14–C17")]
    assert len(ren) == 1, "认知域分工说明行不唯一"
    lines[ren[0]] += (
        "**C97 疑与信**，判「一份凭据被撤销后这笔『曾信／今疑』挂在谁名下、"
        "撤销之权由谁执且可否被反问、疑而未决之部记入哪个科目」——"
        "是 C50 更正回灌在凭据一侧的前置（回灌之前，先问凭据撤下之后账挂在谁名下）；"
    )

    # 来源映射追加一行
    map_idx = [i for i, l in enumerate(lines) if l.strip() == "- C96 ← P97"]
    assert len(map_idx) == 1, "C96 映射行不唯一"
    lines.insert(map_idx[0] + 1, "- C97 ← P98")

    save(p, lines, eol, "计数/映射/心律/导航/分工说明齐更")

# ============ core/part-01.md ============
p = os.path.join(ROOT, "core/part-01.md")
t, eol = load_eol(p)
if "（C97）" in t:
    print("SKIP: part-01 已含 C97")
else:
    lines = t.split(eol)
    old = "**可编辑项九十类**"
    assert t.count(old) == 1, "part-01 计数锚点不唯一"
    t = t.replace(old, "**可编辑项九十一类**", 1)
    lines = t.split(eol)
    c4 = [i for i, l in enumerate(lines) if l.startswith("- **C4 自由 = 可觉知地编辑**")]
    assert len(c4) == 1, "part-01 C4 行不唯一"
    lines[c4[0]] += (
        "91一份凭据被撤销后这笔「曾信／今疑」之记账方位"
        "（原凭据名下／持信者名下／共同体之册）、撤销权之执有者与可反问性、"
        "疑而未决之部的记账科目（C97）。"
    )
    save(p, lines, eol, "C4 计数与清单第 91 项")

# ============ core/part-05.md ============
p = os.path.join(ROOT, "core/part-05.md")
t, eol = load_eol(p)
if "C97 疑与信" in t:
    print("SKIP: part-05 已含 C97")
else:
    lines = t.split(eol)
    hdr = [i for i, l in enumerate(lines) if l.startswith("### 认知 · 语言 · 技术域（C14–C17")]
    assert len(hdr) == 1, "part-05 域标题不唯一"
    lines[hdr[0]] = lines[hdr[0]].replace("、C93）", "、C93、C97）")
    assert "C97" in lines[hdr[0]], "域标题替换失败"
    # 追加条目：末尾保留空行结构，插到最后一个非空行之后
    last = max(i for i, l in enumerate(lines) if l.strip())
    lines.insert(last + 1, C97)
    save(p, lines, eol, "域标题 +C97 与 C97 条目")
