#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觉思者 · 命题卡生成器（scripts/make_card.py）

为什么存在
==========
最省 token 的推广，是让**已经发生的推理自动产出可分发物**。
本脚本把 SKILL.md AUTO_EVOLVE 区内的某条命题，用**模板拼串**渲染成一张静态卡片
（HTML + 可读文本两种形态）。**全程不调用任何模型**，边际成本 ≈ 0。

产出
====
  cards/P<n>.html        单张命题卡（自包含，可直接贴到 GitHub Pages / 社交 / README）
  cards/P<n>.md          同名 Markdown 文本卡（便于贴到 Issue / 论坛 / 邮件）
  cards/index.html       全部命题卡索引（自动扫描 cards/*.html）
  cards/latest.md        「本周最可能被推翻的命题」片段，供 README 顶部引用

用法
====
  python scripts/make_card.py P36         # 生成指定命题卡
  python scripts/make_card.py latest      # 生成编号最大的那张（每轮推演后跑）
  python scripts/make_card.py all         # 重建全部卡片 + 索引
  python scripts/make_card.py P36 --challenger "github用户A" --counter "反例简述"
      # 追加一条「已被挑战」记录（证伪记名制，挑战者永久署名）

设计约束
========
- 零第三方依赖，仅标准库，Windows 可直接运行。
- 只**读** SKILL.md，绝不写回。
- 输出为静态文件，不联网、不依赖任何 CDN，双击即可用。
"""
import os
import re
import sys
import html
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "SKILL.md")
CARDS = os.path.join(ROOT, "cards")
HOOK = "本周最可能被推翻的命题 —— 来推翻它。"

CARD_TPL = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>觉思者 · {pid} {title}</title>
<style>
 body{{margin:0;background:#fbf8f3;font-family:"Songti SC","Noto Serif SC",Georgia,serif;color:#24201c}}
 .wrap{{max-width:760px;margin:0 auto;padding:32px 24px}}
 .card{{background:#fff;border:1px solid #e6ded2;border-radius:12px;padding:26px 28px}}
 .hook{{font-size:12px;letter-spacing:.2em;color:#8a5a2b;text-transform:uppercase}}
 h1{{font-size:24px;margin:8px 0 4px}}
 .pid{{color:#8a5a2b;font-size:14px;letter-spacing:.06em}}
 .sec{{margin-top:18px}}
 .lbl{{font-size:12px;color:#8a8078;letter-spacing:.1em}}
 .body{{font-size:15px;line-height:1.8}}
 ul{{margin:6px 0 0 20px;padding:0}} li{{margin:4px 0;font-size:14px}}
 .foot{{margin-top:22px;padding-top:14px;border-top:1px solid #e6ded2;font-size:12.5px;color:#8a8078}}
 .badge{{display:inline-block;background:#f3e8d8;color:#8a5a2b;border-radius:20px;padding:2px 10px;font-size:12px}}
 .repo{{font-family:Consolas,monospace;font-size:12.5px;background:#f2ece2;padding:2px 6px;border-radius:4px}}
</style></head><body><div class="wrap"><div class="card">
<div class="hook">{hook}</div>
<h1>{title}</h1>
<div class="pid">{pid} · 觉思者 Juesizhe · <span class="badge">可商榷</span></div>
<div class="sec"><div class="lbl">判准</div><div class="body">{core}</div></div>
<div class="sec"><div class="lbl">来源</div><ul>{sources}</ul></div>
<div class="sec"><div class="lbl">可证伪条件</div><div class="body">{falsify}</div></div>
{challenges}
<div class="foot">
一条可被推翻的命题，胜过十句不可讨论的断言。<br>
参与方式：<span class="repo">github.com/juesizhe/juesizhe/issues/new?template=refutation.yml</span>
发布于 {now}
</div>
</div></div></body></html>
"""

MD_TPL = """# {pid} · {title}

> {hook}

**判准**：{core_md}

**来源**：{sources_md}

**可证伪条件**：{falsify_md}

{challenges_md}

—— 觉思者 Juesizhe · 可商榷的跨域哲学命题 ｜ 参与：github.com/juesizhe/juesizhe/issues
"""


# ─────────────────────────── 解析 ───────────────────────────

def load_block():
    text = open(SKILL, encoding="utf-8").read()
    if "<!-- AUTO_EVOLVE_START -->" not in text:
        return {}
    return text.split("<!-- AUTO_EVOLVE_START -->")[1].split("<!-- AUTO_EVOLVE_END -->")[0]


def parse(pid, block):
    """取某条命题的正文块（到下一个 `- P<n+1>` 之前）。"""
    lines = block.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(rf"^\s*-\s+{pid}\s", ln):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\s*-\s+P\d+\s", lines[j]):
            end = j
            break
    head = lines[start]
    title = re.sub(rf"^\s*-\s+{pid}\s+", "", head).replace("（可商榷）", "").strip()
    title = re.split(r"[：:]", title, maxsplit=1)[0].strip() or pid
    if len(title) > 30:
        title = title[:30].rstrip("，,、的之在 ") + "…"
    core = re.split(r"[：:]", re.sub(rf"^\s*-\s+{pid}\s+", "", head), maxsplit=1)
    core = core[1].strip() if len(core) > 1 else ""

    sources, falsify, insight = [], "", ""
    for ln in lines[start + 1:end]:
        s = ln.strip()
        if re.match(r"^[①②③④⑤⑥⑦⑧⑨]", s):
            sources.append(s)
        elif s.startswith("推演新知"):
            insight = s.split("：", 1)[-1].strip()
        elif s.startswith("可证伪"):
            falsify = s.split("：", 1)[-1].strip()
        elif s and not sources and not falsify and not s.startswith("-"):
            core = (core + " " + s).strip()
    return {"pid": pid, "title": title, "core": core, "sources": sources,
            "falsify": falsify, "insight": insight}


def max_pid(block):
    nums = [int(m) for m in re.findall(r"^\s*-\s+P(\d+)\s", block, re.M)]
    return f"P{max(nums)}" if nums else "P0"


# ─────────────────────────── 挑战记录（证伪记名制） ───────────────────────────

def challenges_path():
    return os.path.join(ROOT, "references", "challenges.json")


def load_challenges():
    p = challenges_path()
    if not os.path.exists(p):
        return {}
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


def save_challenges(data):
    p = challenges_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def render_challenges(pid):
    all_c = load_challenges()
    items = all_c.get(pid, [])
    if not items:
        return "", "尚未有人提出有效反例 —— 第一个推翻它的人会永久留名。"
    li = "\n".join(f'<li><b>@{html.escape(c["by"])}</b>：{html.escape(c["text"])}'
                   f' <span style="color:#8a8078">· {c["date"]}</span></li>' for c in items)
    html_part = ('<div class="sec"><div class="lbl">已被挑战</div><ul style="list-style:none;'
                 'margin-left:0;padding-left:0">' + li + "</ul></div>")
    md_part = "**已被挑战**：\n" + "\n".join(
        f'- @{c["by"]}：{c["text"]}（{c["date"]}）' for c in items)
    return html_part, md_part


# ─────────────────────────── 渲染 ───────────────────────────

def render(pid, block):
    d = parse(pid, block)
    if not d:
        return False
    now = datetime.now()
    ch_html, ch_md = render_challenges(pid)
    sources_html = "".join(f"<li>{html.escape(s)}</li>" for s in d["sources"]) or "<li>（待补）</li>"
    html_out = CARD_TPL.format(
        pid=pid, title=html.escape(d["title"]), hook=HOOK,
        now=now.strftime("%Y-%m-%d"),
        core=html.escape(d["core"]) or "（见 SKILL.md 正文）",
        sources=sources_html,
        falsify=html.escape(d["falsify"]) or "（待补）",
        challenges=ch_html,
    )
    md_out = MD_TPL.format(
        pid=pid, title=d["title"], hook=HOOK,
        core_md=d["core"], sources_md="；".join(d["sources"]),
        falsify_md=d["falsify"], challenges_md=ch_md,
    )
    os.makedirs(CARDS, exist_ok=True)
    open(os.path.join(CARDS, f"{pid}.html"), "w", encoding="utf-8").write(html_out)
    open(os.path.join(CARDS, f"{pid}.md"), "w", encoding="utf-8").write(md_out)
    print(f"OK cards/{pid}.html  cards/{pid}.md")
    return True


def build_index():
    if not os.path.isdir(CARDS):
        return
    files = sorted((f for f in os.listdir(CARDS) if re.match(r"^P\d+\.html$", f)),
                   key=lambda s: int(s[1:-5]))
    if not files:
        return
    rows = "\n".join(f'<li><a href="{f}">{f[:-5]}</a></li>' for f in files)
    latest = files[-1][:-5]
    page = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<title>觉思者 · 命题卡</title>
<style>body{{font-family:"Songti SC",serif;background:#fbf8f3;color:#24201c;padding:32px}}
a{{color:#8a5a2b}}</style></head><body>
<h1>觉思者 · 命题卡</h1><p>{HOOK}</p>
<ul>{rows}</ul>
<p><a href="{latest}.html">→ 最新：{latest}</a></p>
</body></html>"""
    open(os.path.join(CARDS, "index.html"), "w", encoding="utf-8").write(page)
    open(os.path.join(CARDS, "latest.md"), "w", encoding="utf-8").write(
        f"<!-- 由 scripts/make_card.py 生成；README 顶部引用此片段 -->\n"
        f"> **{HOOK}**\n>\n"
        f"> 最新：**{latest}** —— 卡片见 cards/{latest}.html ｜ "
        f"推翻它：github.com/juesizhe/juesizhe/issues/new?template=refutation.yml\n")
    print(f"OK cards/index.html （共 {len(files)} 张）  cards/latest.md")


def main():
    argv = sys.argv
    block = load_block()
    if not block:
        print("ERROR: SKILL.md 中未找到 AUTO_EVOLVE 区", file=sys.stderr)
        sys.exit(2)

    if "--challenger" in argv:
        target = argv[1] if len(argv) > 1 else max_pid(block)
        i = argv.index("--challenger")
        who = argv[i + 1]
        counter = argv[argv.index("--counter") + 1] if "--counter" in argv else ""
        data = load_challenges()
        data.setdefault(target, []).append({
            "by": who, "text": counter, "date": datetime.now().strftime("%Y-%m-%d")
        })
        save_challenges(data)
        print(f"OK 已为 {target} 记名挑战者 @{who}（写入 references/challenges.json）")
        if not any(a.startswith("P") or a in ("latest", "all") for a in argv[1:]):
            sys.exit(0)

    cmd = argv[1] if len(argv) > 1 else "latest"
    if cmd == "latest":
        cmd = max_pid(block)
    if cmd == "all":
        nums = sorted({int(m) for m in re.findall(r"^\s*-\s+P(\d+)\s", block, re.M)})
        for n in nums:
            render(f"P{n}", block)
        build_index()
    else:
        if not render(cmd, block):
            print(f"ERROR: 未找到命题 {cmd}", file=sys.stderr)
            sys.exit(1)
        build_index()


if __name__ == "__main__":
    main()
