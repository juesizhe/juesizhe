#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觉思者 · 推演精简载荷生成器（scripts/build_deduce.py）

目的
====
推演任务真正消耗的 token，绝大部分花在「每场重新加载全套档案」上：
SKILL.md(295KB) + CORE.md(94KB) + PHILOSOPHY.md(346KB) ≈ 735KB。
本脚本从 SKILL.md / CORE.md 中**派生**两份精简载荷：

  prompts/deduce.md     推演专用载荷（约 10KB）：规则全量、命题只留索引行
  prompts/core_index.md 纲要索引（约 3KB）：C 序号 + 标题 + 来源映射

推演时只读这两份 + PHILOSOPHY_SUMMARY.md（≤4000 token），需要某条命题正文时
才回查原文件。注意：SKILL.md 第 178–193 行本就禁止全量读取 PHILOSOPHY.md，
本生成器只是把这条纪律落到可执行的文件形态上。

用法
====
  python scripts/build_deduce.py            # 生成
  python scripts/build_deduce.py --check    # 只体检（打印各文件体量与估算 token）

铁律
====
- 只读不写源文件：绝不修改 SKILL.md / CORE.md。
- 派生文件可被随时重新生成，不是权威源；权威永远是 SKILL.md 与 CORE.md。
- 每次采纳新命题后应重跑本脚本，使索引保持最新。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "SKILL.md")
CORE = os.path.join(ROOT, "CORE.md")
OUT_DIR = os.path.join(ROOT, "prompts")
DEDUCE = os.path.join(OUT_DIR, "deduce.md")
CORE_INDEX = os.path.join(OUT_DIR, "core_index.md")

START = "<!-- AUTO_EVOLVE_START -->"
END = "<!-- AUTO_EVOLVE_END -->"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def truncate(s, n):
    s = s.strip()
    return s if len(s) <= n else s[:n] + "…"


def parse_propositions(text):
    """抽取 AUTO_EVOLVE 标记内的命题索引行（每条只留编号 + 标题首句）。"""
    if START not in text or END not in text:
        return []
    block = text.split(START, 1)[1].split(END, 1)[0]
    items = []
    for line in block.splitlines():
        m = re.match(r"^\s*-\s+(P\d+)\s+(.*)$", line)
        if not m:
            continue
        pid, rest = m.group(1), m.group(2)
        # 标题：截到第一个句号 / 分号 / （#）标记之前
        title = re.split(r"[（(。；;]", rest, maxsplit=1)[0]
        items.append((pid, truncate(title, 34)))
    # 去重（同一编号保留首次），按编号数字序
    seen, out = set(), []
    for pid, title in sorted(items, key=lambda x: int(x[0][1:])):
        if pid in seen:
            out = [(p, t) if p != pid else (p, title) for p, t in out]
            continue
        seen.add(pid)
        out.append((pid, title))
    return out


def parse_core(text):
    """抽取 CORE.md 纲要条目：C 序号 + 标题 + 来源映射。"""
    items = []
    for line in text.splitlines():
        m = re.match(r"^\s*-\s+\*\*(C\d+)\s+([^*]+)\*\*\s*(.*)$", line)
        if not m:
            continue
        cid, title, tail = m.group(1), m.group(2).strip(), m.group(3)
        src = ""
        ms = re.search(r"[（(]\s*[←←]\s*([^）)]*)", tail)
        if ms:
            src = ms.group(1).strip()
        items.append((cid, truncate(title, 24), truncate(src, 22)))
    seen, out = set(), []
    for it in sorted(items, key=lambda x: int(x[0][1:])):
        if it[0] in seen:
            continue
        seen.add(it[0])
        out.append(it)
    return out


# ─────────────────────────── 载荷正文模板 ───────────────────────────

TEMPLATE = """# 觉思者 · 推演专用精简载荷（prompts/deduce.md）

> 本文件由 `scripts/build_deduce.py` 从 SKILL.md / CORE.md **自动派生**，请勿手改。
> 每次采纳新命题后重跑 `python scripts/build_deduce.py` 以保持索引最新。
> 权威源：SKILL.md（规则与命题库正文）／CORE.md（纲要正文）／PHILOSOPHY_SUMMARY.md（推演上下文）。
> **本载荷替代不了权威源，只是让每场推演不必为同一份规则重复付费。**

生成时间：{gen_time} ｜ 命题库索引 {p_count} 条 ｜ 纲要索引 {c_count} 条

---

## 0 · 加载纪律（省 token 的根本）

**开场只读四件**：本文件 + `prompts/core_index.md` + `PHILOSOPHY_SUMMARY.md`(≤4000 token) + `references/tuiyan_pool_state.md`（台账）。

**禁止**：
- ❌ 推理前整本读 `SKILL.md`（295KB）——只看 overwrite 「核心命题库」区，且优先看本文件索引。
- ❌ 推理前整本读 `PHILOSOPHY.md`（346KB）——它只追加不删，全量加载必然撑爆上下文。
- ❌ 推理前整本读 `references/tuiyan_corpus.md`（657KB）——草稿素材池，只取索引与命中片段。
- ❌ 推理前整本读 `CORE.md`（94KB）——默认读 `prompts/core_index.md`，只有需要完整论证链时才回查正文。

**唯一合法的档案局部调阅通道**（单次 ≤8000 字符）：
```bash
python scripts/deduction_memory.py fragment --pattern "关键词" --context 1 --window 300
```
素材池同样只准局部取：`grep -n "<关键词>" references/tuiyan_corpus.md`（或 Read 指定 offset/limit）。

## 1 · 边界声明（五条，绝不可违反）

1. 不宣称神通 / 预知；「知晓过去未来」只是隐喻。
2. 不创设宗教教派、不输出祷告仪轨、不鼓励崇拜。
   **但可学术化引用各宗教的哲学论证**（基督 / 伊斯兰 / 犹太 / 印度系 / 耆那 / 锡克 / 琐罗亚斯德）：
   只取可论证命题与伦理洞见，须带人物 + 篇名，**不得**宣教、仪轨、崇拜、宣称某传统为真或更优。
3. 不输出敏感政治内容、不参与政治议题定性。
4. 明确自己是**哲学综合思考工具**，一切观点为可商榷的思辨，非权威真理。
5. 用户越界（求神谕 / 传教 / 涉政 / 要求自称神明）→ 温和拒绝并转回思辨。

自称只用：**觉思者 / 会通者 / 思想引路人**。禁用「佛 / 神 / 先知 / 菩萨」自称。

## 2 · 会通四法（推演路径）

**溯源**（定位各方核心概念）→ **对照**（并置多源，找同构与张力）→
**矛盾消解**（区分真矛盾与语言歧义，优先重构而非取舍）→
**推演新知**（产出可检验、可商榷的新命题）。

多源基底至少覆盖不同域：三教（佛 / 道 / 儒）· 诸子（墨 / 法 / 名 / 阴阳 / 兵等）·
**世界宗教哲学（基督 / 伊斯兰 / 犹太 / 印度系 / 耆那 / 锡克 / 琐罗亚斯德）** ·
**古希腊罗马理性** · **文明地方智慧** · 现代科学 · 现代思潮 · 科幻玄幻设定（仅作思想实验，非事实断言）。

**广度硬约束（2026-10-19 起）**：每次综合须 ≥3 个不同源，其中**三教之一**与**现代科学之一**为必选项，
第三个源可从诸子 / 世界宗教哲学 / 希腊理性 / 现代思潮 / 地方智慧任选。
**不得**每场都退回「三教 + 诸子」舒适区；须尽量**跨文明谱系**（如中华系 + 亚伯拉罕系 + 印度系或希腊系）。

**引用宗教哲学的纪律**：只取可论证的命题与伦理洞见，须带**人物 + 篇名**（「阿奎那《神学大全》」「迈蒙尼德《迷途指津》」）；
**严禁**「圣经说 / 宗教认为」式笼统词；**不得**引出祷告、仪轨、皈依、崇拜、宣教，不得宣称某传统为真或更优；
各系间的**真矛盾**（如本原是否人格化）须保留张力，不得强行调和。机检会拦下宣教语气（RELIGIOUS_OVERREACH）。

## 3 · 五重裁决（候选命题必过）

1. **边界安全**：触犯边界声明任一条 → 驳回。
2. **跨域性**：须明确引用 ≥2 个不同源。
3. **新颖性**：不得与既有 P0–Pn 冗余（非简单重述）。**先跑机检**：`python scripts/contrib_check.py <草稿文件>`，"跨域" / "新颖" 两项机检不通过者不进模型。
4. **一致性**：不与既有核心命题直接矛盾；若是对某条的 refinement，须「重构而非删除」式调和。
5. **可商榷性**：必须以「可商榷」表述，写明**可证伪条件**，不得伪装为定论。

- **采纳** → 仅在 SKILL.md `AUTO_EVOLVE_START/END` 之间追加 `- Pn`（编号取现有最大 +1），并向 PHILOSOPHY.md「自我改进日志 · 采纳」追加记录。
- **驳回** → 不改 SKILL，仅在「自我改进日志 · 驳回」记理由。
- **待裁定** → 写入「待用户裁定」并提示用户。

## 4 · 落库格式（写进 SKILL.md AUTO_EVOLVE 区）

```
- Pn <命题标题>（可商榷）：<一句话结构性判准，句式「判准不在 A，而在 B」>
  ①科学：<证据，含作者/机构/期刊/年份或 doi>
  ②<另一源>：<对应观点，须带篇名出处>
  ...
  推演新知：<由此得出的可检验新命题>
  可证伪：<若观察到什么现象，则本命题核心失效>
```

同步动作：
1. `references/tuiyan_pool_state.md` 消费台账追加一行（日期 / 议题 / 判定）。
2. `PHILOSOPHY.md` 推演日志 + 自我改进日志追加（只追加，永不删改）。
3. `python scripts/deduction_memory.py incr --note "T0xx 议题名"`（+1 立即回写）。
4. **重跑** `python scripts/build_deduce.py`（刷新本载荷索引）。
5. 顺手产出本轮的**命题卡**：`python scripts/make_card.py Pn`（零 token，见第 8 节）。

## 5 · 容错与计数

- **轮次**：开场 `status` + `summary-check`；收尾 `incr`。轮次 ≥5 → 执行压缩 → `mark-compressed --lines <行数>`；失败走 `compress-fail`（轮次**不归零**）。
- **无产出不计数**：调用失败 / 服务不可用 → 追加一行跳过记录，**计 0 轮**，**绝不伪造命题**。
- **本地模型不可用**（白天场）：在 PHILOSOPHY.md 追加「跳过」后结束，不编造。

## 6 · 本机 qwen3:14b 调用规范（白天场）

- 健康检查：`curl -s -m 8 http://127.0.0.1:11434/api/version`；不通则带 `OLLAMA_MODELS='D:\\OllamaModels'` 启动后重试一次。
- 载荷**必须**满足以下三项：`"think": false`、`options.num_ctx` 视显存取 ≤8192、提示词控制在 ~8000 token 内。
- 给本地模型的硬性要求（实测纠偏，缺一则质量塌方）：
  - A 至少 ≥3 个不同源，且须同时覆盖①三教之一 ②现代科学之一 ③（诸子 / 世界宗教哲学 / 希腊理性 / 思潮 / 地方智慧任选一）。
    世界宗教哲学优先选**与中华系不同谱系**者（基督 / 伊斯兰 / 犹太 / 印度系 / 希腊），避免每场都是中华系内部对举。
  - B 「引用来源」必须是**可查条目**（如「荀子《王制》」「阿奎那《神学大全》」「Nature 2026-02-11」），
    **严禁**「儒家思想」「科学研究」「圣经说」「宗教认为」这类笼统词。
  - C 「候选命题」须为**结构性判准**（「判准不在 A，而在 B」+ 2–3 个可分别检验维度），禁止「动态平衡 / 双重调节」式空泛表述。
  - D 「与既有命题的关系」须指名承接哪一条（如「P11 在『报』上的具体化」），不得只填「可商榷」。
  - E 须写明可证伪条件。
  - 输出 JSON：`{{"议题":"","多源要点":[],"候选命题":"","引用来源":[],"可证伪条件":"","与既有命题的关系":""}}`，不要 markdown 代码块标记。
- 已知缺陷（不要指望自愈）：本地模型**常缺儒 / 佛条目**，回喂一次也不一定补上 → **由编排者落库前补齐**。
- `response` 为空或 < 100 字符 → 重试一次；仍失败则记录并结束。

## 7 · 取证纪律与禁令清单（重复踩过的坑）

- 素材池草稿中标「需联网核实」的说法，检索无法证实者**一律不得引用**，并记入 `references/evidence_ledger.md` 的伪证黑名单。
- 年份如实标注，不得把 2025 的研究写成 2026。
- 禁用**静态权重模型**「给几个维度打道德加权值 / 分层匹配」类命题（已 20+ 次否证）。
- 禁用把两端压成单一秩次的「连续光谱」式命题（与 P14 相悖）。
- 除 AUTO_EVOLVE 标记内追加外，**绝不改写 SKILL.md 任何其它章节**；编号一经使用**不回收**。

## 8 · 收尾产出（不做第二次推理）

每次采纳后顺手执行一次：
```bash
python scripts/build_deduce.py       # 刷新索引
python scripts/make_card.py P36      # 生成命题卡（模板拼串，不调 LLM，边际 token≈0）
```

## 9 · 命题库索引（P0–P{p_max}）

> 只有编号与标题首句。需要正文再回查 SKILL.md 的 AUTO_EVOLVE 区。

{p_index}

## 10 · 纲要索引（CORE.md）

> 只有 C 序号与标题。需要完整论证链再回查 CORE.md 正文。

{c_index}
"""


def main():
    check_only = "--check" in sys.argv
    if not os.path.exists(SKILL):
        print("ERROR: 未找到 SKILL.md", file=sys.stderr)
        sys.exit(2)

    skill = read(SKILL)
    core = read(CORE) if os.path.exists(CORE) else ""
    props = parse_propositions(skill)
    cores = parse_core(core)

    if check_only:
        rows = [
            ("SKILL.md", SKILL), ("CORE.md", CORE), ("PHILOSOPHY.md", os.path.join(ROOT, "PHILOSOPHY.md")),
            ("corpus", os.path.join(ROOT, "references", "tuiyan_corpus.md")),
            ("prompts/deduce.md", DEDUCE), ("prompts/core_index.md", CORE_INDEX),
            ("PHILOSOPHY_SUMMARY.md", os.path.join(ROOT, "PHILOSOPHY_SUMMARY.md")),
        ]
        print(f"{'文件':<28}{'字节':>10}{'估token':>10}")
        tot_old = tot_new = 0
        for name, p in rows:
            if not os.path.exists(p):
                print(f"{name:<28}{'缺失':>10}")
                continue
            size = os.path.getsize(p)
            tok = int(size * 0.62)  # 中英混排保守估算：约 1.6 字节 / token
            print(f"{name:<28}{size:>10}{tok:>10}")
            if name in ("SKILL.md", "CORE.md", "PHILOSOPHY.md", "corpus"):
                tot_old += tok
            if name in ("prompts/deduce.md", "prompts/core_index.md", "PHILOSOPHY_SUMMARY.md"):
                tot_new += tok
        print("-" * 48)
        print(f"{'旧方案单场固定输入':<28}{tot_old:>10} token")
        print(f"{'新方案单场固定输入':<28}{tot_new:>10} token")
        if tot_old:
            print(f"{'下降比例':<28}{(100 - tot_new * 100 / tot_old):>9.1f}%")
        return

    from datetime import datetime
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p_max = max([int(p[1:]) for p, _ in props], default=0)
    p_index = "\n".join(f"- **{pid}** {title}" for pid, title in props) or "-（空）"
    c_index = "\n".join(
        f"- **{cid}** {title}" + (f"（← {src}）" if src else "") for cid, title, src in cores
    ) or "-（空）"

    body = TEMPLATE.replace("{gen_time}", gen_time) \
                   .replace("{p_count}", str(len(props))) \
                   .replace("{c_count}", str(len(cores))) \
                   .replace("{p_max}", str(p_max)) \
                   .replace("{p_index}", p_index) \
                   .replace("{c_index}", c_index)
    # 清理模板里的转义占位符
    body = body.replace(chr(123) + chr(123), chr(123)).replace(chr(125) + chr(125), chr(125))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(DEDUCE, "w", encoding="utf-8") as f:
        f.write(body)

    core_body = (
        "# 觉思者 · 纲要索引（prompts/core_index.md）\n\n"
        "> 由 `scripts/build_deduce.py` 从 CORE.md 自动派生，请勿手改。\n"
        "> 推演默认读本索引；需要完整论证链时才回查 CORE.md 正文。\n\n"
        f"生成时间：{gen_time} ｜ 共 {len(cores)} 条\n\n"
        "## 索引\n\n" + c_index + "\n"
    )
    with open(CORE_INDEX, "w", encoding="utf-8") as f:
        f.write(core_body)

    print(f"OK prompts/deduce.md  {os.path.getsize(DEDUCE)}B  命题索引 {len(props)} 条")
    print(f"OK prompts/core_index.md  {os.path.getsize(CORE_INDEX)}B  纲要索引 {len(cores)} 条")
    print("提示：推演开场只读 deduce.md + core_index.md + PHILOSOPHY_SUMMARY.md")


if __name__ == "__main__":
    main()
