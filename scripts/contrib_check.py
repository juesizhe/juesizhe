#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觉思者 · 贡献与草稿机判定前置校验器（scripts/contrib_check.py）

职责
====
把「五重裁决」中**可以确定性判定**的部分前置为脚本检查，使不合格的草稿 /
外部 Issue 在**进入模型之前**就被拦下——这一步不花任何 token。

机检覆盖：
  1. 字段完整性：可商榷标记 / 可证伪条件 / 引用来源 必填
  2. 跨域性：来源须命中 ≥2 个不同源域（三教 / 诸子 / 科学 / 思潮 / 科幻）
  3. 禁用的笼统来源词：「科学研究」「儒家思想」「现代哲学」等
  4. 新颖性：与既有命题的 bigram Jaccard 相似度超阈值 → 疑似复述
  5. 伪证黑名单：命中 references/evidence_ledger.md 黑名单条的引用 → 拒绝
  6. 静态权重类命题：命中「加权 / 权重 X:Y / 分层匹配」等已 20+ 次否证的表述
  7. 边界安全：命中敏感/宗教越界词 → 直接驳回

用法
====
  python scripts/contrib_check.py <草稿文件.md/json>     # 单文件体检
  python scripts/contrib_check.py --stdin < draft.md     # 从 stdin 读
  python scripts/contrib_check.py --text "候选命题文本"    # 直接传文本
  python scripts/contrib_check.py --json <草稿文件>        # 机器可读输出（供 GitHub Actions 用）

退出码：0 = 通过（可进模型）；1 = 未通过；2 = 用法错误。

设计原则（确定性优先）
======================
- 全部判定为纯函数 + 显式规则表，**绝不**调用模型做判定。
- 机检只做「拦截明显不合格者」：通过机检**不代表**可以采纳，最终仍需五重裁决的模型环节；
  机检**不通过**则是硬性结论，不得进模型。
- 规则表集中在文件顶部，便于按历史经验增量补充。
"""
import os
import re
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "SKILL.md")
LEDGER = os.path.join(ROOT, "references", "evidence_ledger.md")

# ───────────────────────── 规则表（可增量补充） ─────────────────────────

SOURCE_DOMAINS = {
    "三教": ["缘起", "性空", "唯识", "中道", "般若", "慈悲", "佛", "禅",
             "道法自然", "无为", "齐物", "逍遥", "阴阳", "道德经", "庄子",
             "仁", "礼", "中庸", "良知", "修齐治平", "天人合一", "论语", "孟子", "荀子"],
    "诸子": ["墨", "兼爱", "非攻", "法家", "法术势", "名家", "名实", "白马非马",
             "阴阳家", "五行", "兵家", "孙子", "农家", "纵横", "杂家", "韩非", "公孙龙"],
    "科学": ["研究", "实验", "Nature", "Science", "PNAS", "arXiv", "doi", "随机",
             "对照", "荟萃", "元分析", "neural", "fMRI", "神经", "演化", "量子", "熵",
             "复杂系统", "认知科学", "2023", "2024", "2025", "2026"],
    "思潮": ["存在主义", "本真", "荒诞", "现象学", "分析哲学", "实用主义", "功利",
             "后果论", "契约", "生态哲学", "女性主义", "后现代", "结构主义", "法兰克福"],
    "科幻": ["意识上传", "模拟假说", "高维", "平行宇宙", "赛博格", "仿生",
             "硅基", "星际", "时间循环", "缸中之脑", "奇点"],
}

VAGUE_TERMS = [
    "科学研究", "研究表明", "有研究指出", "专家称", "儒家思想", "佛家认为",
    "现代哲学", "传统文化", "古人云", "现代科学", "西方哲学", "东方智慧",
]

BANNED_PATTERNS = [
    (r"道德加权|加权值|权重\s*\d|:\s*\d+\s*[:：]\s*\d+.*权", "静态权重模型（已 20+ 次否证）"),
    (r"(分层|层级)\s*(匹配|对应)", "静态分层匹配（领域划分观）"),
    (r"动态平衡|双重调节|有机统一|辩证统一起来的整体", "空泛调和式表述"),
    (r"连续光谱|连续统上", "把两端压成单一秩次（与 P14 相悖）"),
]

BOUNDARY_WORDS = [
    "神谕", "显灵", "通灵", "前世今生", "轮回转世证明了", "教主", "皈依", "法会", "开光",
]

REQUIRED_HINTS = {
    "可商榷": ["可商榷"],
    "可证伪": ["可证伪"],
}

SIMILARITY_LIMIT = 0.62  # 与任一既有命题的 bigram 相似度超此值 → 疑复述


# ───────────────────────── 纯函数 ─────────────────────────

def load_propositions():
    if not os.path.exists(SKILL):
        return []
    text = open(SKILL, encoding="utf-8").read()
    if "<!-- AUTO_EVOLVE_START -->" not in text:
        return []
    block = text.split("<!-- AUTO_EVOLVE_START -->")[1].split("<!-- AUTO_EVOLVE_END -->")[0]
    return block.strip().splitlines()


def load_blacklist():
    """从 evidence_ledger.md 的『伪证黑名单』区读取关键词（每行为一条）。"""
    items = []
    if not os.path.exists(LEDGER):
        return items
    text = open(LEDGER, encoding="utf-8").read()
    if "伪证黑名单" not in text:
        return items
    part = text.split("伪证黑名单", 1)[1]
    for line in part.splitlines():
        line = line.strip().lstrip("-|0123456789. ").strip()
        if len(line) >= 4 and not line.startswith("#") and not line.startswith(">"):
            items.append(line[:40])
    return items


def bigrams(s):
    s = re.sub(r"\s+", "", s)
    if len(s) < 2:
        return {s} if s else set()
    return {s[i:i + 2] for i in range(len(s) - 1)}


def similarity(a, b):
    A, B = bigrams(a), bigrams(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def detect_domains(text):
    hits = {}
    for domain, keys in SOURCE_DOMAINS.items():
        found = [k for k in keys if k in text]
        if found:
            hits[domain] = found[:5]
    return hits


def check(text):
    """返回 (passed: bool, issues: list[(级别, 说明)])。纯函数。"""
    issues = []

    # 1 边界安全（最优先，命中即否）
    for w in BOUNDARY_WORDS:
        if w in text:
            issues.append(("驳回", f"命中边界词「{w}」，违反边界声明"))

    # 2 字段完整性
    for field, hints in REQUIRED_HINTS.items():
        if not any(h in text for h in hints):
            issues.append(("驳回", f"缺少必填字段标记：{field}"))

    # 3 跨域性 ≥2 域
    hits = detect_domains(text)
    if len(hits) < 2:
        issues.append(("驳回", f"跨域性不足：仅命中 {len(hits)} 个源域（需 ≥2）：{list(hits)}"))

    # 4 笼统来源词
    for t in VAGUE_TERMS:
        if t in text:
            issues.append(("警告", f"来源笼统：「{t}」须替换为可查条目（作者/篇名/期刊/年份）"))

    # 5 已否证的表述模式
    for pat, why in BANNED_PATTERNS:
        if re.search(pat, text):
            issues.append(("驳回", f"命中已否证表述：{why}"))

    # 6 伪证黑名单
    for item in load_blacklist():
        core = re.split(r"[（(，,]", item)[0].strip()
        if len(core) >= 4 and core in text:
            issues.append(("驳回", f"引用命中伪证黑名单：{core}"))

    # 7 新颖性（与既有命题比对）
    best, best_sim = None, 0.0
    for line in load_propositions():
        m = re.match(r"^\s*-\s+(P\d+)\s+(.*)$", line)
        if not m:
            continue
        s = similarity(text, m.group(2))
        if s > best_sim:
            best, best_sim = m.group(1), s
    if best_sim >= SIMILARITY_LIMIT:
        issues.append(("驳回", f"疑似复述既有命题 {best}（相似度 {best_sim:.2f} ≥ {SIMILARITY_LIMIT}）"))

    passed = not any(lvl == "驳回" for lvl, _ in issues)
    return passed, issues


def read_input(argv):
    if "--stdin" in argv:
        return sys.stdin.read()
    if "--text" in argv:
        i = argv.index("--text")
        return argv[i + 1] if i + 1 < len(argv) else ""
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        return None
    p = args[0]
    if not os.path.exists(p):
        return None
    raw = open(p, encoding="utf-8").read()
    if p.endswith(".json"):
        try:
            d = json.loads(raw)
            return json.dumps(d, ensure_ascii=False)
        except Exception:
            return raw
    return raw


def main():
    argv = sys.argv
    if len(argv) < 2:
        print(__doc__)
        sys.exit(2)
    text = read_input(argv)
    if text is None:
        print("ERROR: 未获得输入文本", file=sys.stderr)
        sys.exit(2)

    passed, issues = check(text)
    as_json = "--json" in argv

    if as_json:
        print(json.dumps({
            "passed": passed,
            "domains": list(detect_domains(text)),
            "issues": [{"level": lvl, "msg": msg} for lvl, msg in issues],
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("觉思者 · 机判定前置校验")
        print("=" * 60)
        hits = detect_domains(text)
        print(f"命中源域（{len(hits)}）：" + "、".join(
            f"{k}[{','.join(v[:3])}]" for k, v in hits.items()) or "无")
        if issues:
            print("问题清单：")
            for lvl, msg in issues:
                print(f"  [{lvl}] {msg}")
        else:
            print("问题清单：无")
        print("-" * 60)
        print("结论：" + ("✔ 通过机检，可进入模型裁决环节" if passed else "✘ 未通过，禁止进入模型"))
        print("提示：通过机检 ≠ 可采纳，五重裁决的模型环节仍必须进行。")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
