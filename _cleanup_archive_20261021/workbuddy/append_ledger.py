#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""向 references/evidence_ledger.md 追加本场可引用证据与 3 则伪证黑名单。"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "references", "evidence_ledger.md")
text = open(P, encoding="utf-8").read()

new_evidence = """- 审美评价由「视觉语义」与「享乐价值」两条可分离通路承载（r=0.83 / 0.65，可泛化到 HCP 100 人独立数据集），且默认模式网络对该二维空间的编码强度随视觉艺术专业训练上升 ｜ 出处：Liang 等，*Nature Communications* 2026，DOI 10.1038/s41467-026-73153-6 ｜ 域：科学 ｜ 首次采用：2026-10-17（P37）
- 市场价值相同的「助手复制品」在历史评价上被打低而在美学评价上与原作无差别，且该效应只对艺术生效、对同值家具不生效 ｜ 出处：Newman & Bloom，*J Exp Psychol Gen* 2012;141(3):558–569，DOI 10.1037/a0026035（**年份纠偏：非近年**） ｜ 域：科学 ｜ 首次采用：2026-10-17（P37）
- 刺激完全相同时 AI 标签压低美／深度／创造力／技巧／货币价值评分，而盲评中机器文本反而常更受偏好（SHL0MS 2026 莫奈事件） ｜ 出处：Hutson，*The Monet Test*，Zenodo 2026（record 21788635） ｜ 域：思潮 ｜ 首次采用：2026-10-17（P37）
- 前沿智能体在人类耗时 <4 分钟的任务上成功率近 100%、在 >4 小时的任务上不足 10%，且官方明写其仍不能独立完成实质性项目 ｜ 出处：METR，*Measuring AI Ability to Complete Long Tasks*，2025-03 首版 / NeurIPS 2025 / Time Horizon 1.1 ｜ 域：科学 ｜ 首次采用：2026-10-17（P38）
- AI 预测精度逼近精英人类预报者（ForecastBench 差约 0.017 Brier Index；2026-09-05 bot 首夺 Metaculus Cup）却几乎不做显式 pre-mortem ｜ 出处：ForecastBench（Forecasting Research Institute）与 Metaculus Cup，2026，**经二手转述** ｜ 域：科学 ｜ 首次采用：2026-10-17（P38）
- AI 自主性升高时责备与可预见性仍归于人类；系统拆为「语言模型＋智能体工具」后责任迁移到智能体层 ｜ 出处：《Human Attribution of Causality to AI Across Agency, Misuse, and Misalignment》2026-03，**经二手转述** ｜ 域：科学 ｜ 首次采用：2026-10-17（P38）
- 道德判断共享一片网络而与心智化网络重叠，但各道德基础各有不同激活模式、不存在单一「道德热点」 ｜ 出处：Hopp 等，*Nature Human Behaviour* 2023，DOI 10.1038/s41562-023-01693-8 ｜ 域：科学 ｜ 首次采用：2026-10-17（P39）
- 意图与人身力对道德可接受度的效应跨文化普遍（45 国 27,502 人） ｜ 出处：Bago 等，*Nature Human Behaviour* **2022**，DOI 10.1038/s41562-022-01319-5 ｜ 域：科学 ｜ 首次采用：2026-10-17（P39）
- AI 主体的道德决策被判更不可允许（g=−0.08），而感知心智能力显著削弱并反转该效应（g=+0.11） ｜ 出处：Hill-Cousins、Sweetman & Lowe，2026 预注册元分析，OSF DOI 10.31234/osf.io/stcej_v1（PROSPERO CRD420251237117） ｜ 域：科学 ｜ 首次采用：2026-10-17（P39）
- 道德理由的检测正确率始终 <75%、最难情境中机器所写反而更受偏好，但只要「相信是 AI 写的」就少同意（罚在被感知的作者） ｜ 出处：Garcia、Qian & Palminteri，*PLOS ONE* 2026-08-05，DOI 10.1371/journal.pone.0353391 ｜ 域：科学 ｜ 首次采用：2026-10-17（P39）
"""

new_blacklist = """- 2021《自然·人类行为》无功利审美时 DMN 与 ECN 同时激活（T034 草稿｜检索无法证实；可见者为 Liang 等 *Nat Commun* 2026 之两条可分离通路）
- 2023 联合国数字合作高级别小组《全球数字未来报告》62% / 74% / 重合度 30%（T035 草稿｜检索无法证实；可查者为该小组 2019 报告与 2024 全球数字契约，无此三项数据）
- 2023《Nature Human Behaviour》跨 27 文化道德判断元研究（T036 草稿｜检索无法证实；近邻为 Bago 等 2022 之「文化普遍性」，结论方向相反）
"""

# 证据追加到「> 用法：」提示之前（即第一区块末尾）
anchor = "> 用法：推演开场先用"
i = text.index(anchor)
text = text[:i] + new_evidence + "\n" + text[i:]

# 黑名单追加到「伪证黑名单」区块末尾（--- 之前）
marker = "---\n\n## 三、维护纪律"
j = text.index(marker)
text = text[:j] + new_blacklist + "\n" + text[j:]

open(P, "w", encoding="utf-8", newline="").write(text)
print("OK evidence_ledger 更新；字节", len(text))
