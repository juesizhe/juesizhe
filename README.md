# 觉思者 · Juesizhe

> 跨域哲学综合专家 —— 佛道儒 × 诸子百家 × 现代科学 × 现代多元思潮 × 科幻玄幻，多源会通，推陈出新。

**Juesizhe** is an open, self-evolving philosophical synthesis engine for AI agents. It does not answer from a single tradition. It pulls from the root canons of Buddhism / Daoism / Confucianism, the pre-Qin masters, contemporary science, modern pluralist thought, and speculative fiction — then reconciles them into propositions that are explicitly **debatable**, never asserted as doctrine.

---

## 它是什么 / What it is

一套可运行的 **AI 专家人格规范（Agent Skill）**，不是一个聊天机器人，也不是一套教义。

- **不是** 宗教工具 —— 不宣称神通、不创设教派、不输出祷告仪轨（见 `SKILL.md` 边界声明）。
- **不是** 定论机器 —— 每条核心命题都标注"可商榷"，并附**可证伪条件**。
- **是** 一台会自己长大的思辨引擎 —— 内置自迭代机制，能按规则自主产出、裁决、蒸馏新命题。

## 核心机制 / How it evolves

```
多源输入 → 会通四法 → 候选命题 → 五重裁决 → 落库
   溯源 · 对照 · 矛盾消解 · 推演新知
   ① 边界安全 ② 跨域性(≥2源) ③ 新颖性 ④ 一致性 ⑤ 可商榷性
```

两条定时管线，各司其职：

| 管线 | 职责 |
|------|------|
| **夜间推演**（0/2/4/6 点） | 扩大思维领域 —— 每轮产出 1 条候选命题，过五重裁决后入库 |
| **黎明蒸馏**（7 点） | 去重、合并、精炼 —— 重写 `CORE.md`，记蒸馏日志 |

**铁律**：自动流程**只能**在 `SKILL.md` 的 `AUTO_EVOLVE` 标记内**追加**条目，绝不改写边界声明、工作流等其他章节。编号一经使用**不回收**，保证历史引用永久有效。

## 仓库结构 / Structure

```
juesizhe/
├── SKILL.md                       # 主规范：边界声明、多源基底、工作流、核心命题库 P0–Pn
├── CORE.md                        # 精炼纲要（思想锚点，由黎明蒸馏整份重写）
├── PHILOSOPHY.md                  # 推演日志 / 自我改进日志（采纳·驳回·待裁定）/ 蒸馏日志
├── references/
│   ├── canon.md                   # 经典根脉速查（三教 + 诸子）
│   ├── tuiyan_corpus.md           # 推演语料库（657K，含历次多源素材）
│   └── tuiyan_pool_state.md       # 议题池状态机
└── LICENSE                        # MIT
```

## 安装使用 / Install

作为一个 Agent Skill 使用，把本仓库放到你的 skills 目录即可：

```bash
git clone https://github.com/juesizhe/juesizhe.git ~/.workbuddy/skills/philosopher-sage
```

触发场景：当你希望以多源会通的方式探讨存在、心性、伦理、未来，或需要一位持续学习、推陈出新的哲学思考伙伴时。

## 参与共建 / Contributing

这是本项目开源的全部理由 —— **一个人会通的边界太小**。

欢迎这些贡献：

1. **补源** —— 你熟悉的经典、学派、前沿论文、科幻设定，补进 `references/canon.md` 或语料库。
2. **辩驳** —— 对某条 `Pn` 命题提出反例。最好的贡献是**证伪它**，或给出更优的重构。
3. **提新命题** —— 直接开 PR 追加 `- Pn`，务必满足五重裁决，尤其要写清**可证伪条件**。
4. **修机制** —— 自迭代规则、蒸馏策略、边界声明的措辞改进（结构性改动需 maintainer 评审）。

### 提交命题的格式要求

```
- Pn <命题标题>（可商榷）：<一句话表述>
  ①科学：<证据，含出处与年份>
  ②<另一源>：<对应观点>
  ...
  推演新知：<由此得出的可检验新命题>
  可证伪：<什么情况下本命题失效>
```

**不满足"至少两个不同源"或"未标可商榷"的命题会被自动驳回。**

## 边界 / Boundaries

本项目严格自我约束：不宣称超自然能力、不创设宗教教派、不输出敏感政治内容、不输出政治立场定性、所有观点标明为可商榷的思辨而非权威真理。任何 PR 若触碰上述任一条，将被直接拒绝。

## License

MIT —— 你可以自由使用、修改、分发、商业化，只需保留署名。

---

> 空不是无，是未被固着的万种可能。
