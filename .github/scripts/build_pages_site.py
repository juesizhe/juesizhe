#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建命题卡静态站点（供 GitHub Pages 使用）

为什么独立成脚本：把它塞进 workflow 的 heredoc 会因为 HTML 字面量顶格
而导致 YAML 块标量解析失败。独立文件既可读，也可本地先跑一遍验证。

用法：在仓库根目录执行
    python .github/scripts/build_pages_site.py
产出 _site/（index.html + 全部 cards 内容）
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CARDS = os.path.join(ROOT, "cards")
SITE = os.path.join(ROOT, "_site")

HOOK = "本周最可能被推翻的命题 —— 来推翻它。"
REFUTE = "https://github.com/juesizhe/juesizhe/issues/new?template=refutation.yml"
SOURCE = "https://github.com/juesizhe/juesizhe/issues/new?template=bu-yi-wei.yml"

PAGE_HEAD = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>觉思者 · 可被推翻的命题</title>
<style>
body{font-family:"Songti SC","Noto Serif SC",Georgia,serif;background:#fbf8f3;color:#24201c;
     max-width:760px;margin:0 auto;padding:48px 24px;line-height:1.85}
h1{font-size:28px;margin:0 0 4px}
.eyebrow{font-size:12px;letter-spacing:.24em;color:#8a5a2b;text-transform:uppercase}
.card{border:1px solid #e6ded2;background:#fff;border-radius:12px;padding:22px 24px;margin-top:20px}
a{color:#8a5a2b}
ul{columns:2;column-gap:28px;margin:0;padding-left:18px}
li{margin:3px 0}
code{background:#f2ece2;padding:1px 5px;border-radius:4px;font-size:12.5px}
.foot{margin-top:30px;font-size:12.5px;color:#8a8078}
@media (max-width:600px){ul{columns:1}}
</style></head><body>
<div class="eyebrow">Juesizhe · propositions that invite refutation</div>
<h1>觉思者 · 可被推翻的命题</h1>
<p>这里每一条都写明了自己的失效条件。最好的参与方式不是同意，而是<strong>推翻它</strong>——
第一个给出有效反例的人会永久留名在该命题上。</p>
"""

PAGE_MID = '<div class="card"><ul>{rows}</ul></div>\n'


def main():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE, exist_ok=True)

    files = sorted((f for f in os.listdir(CARDS) if re.match(r"^P\d+\.html$", f)),
                   key=lambda s: int(s[1:-5]))
    for f in files:
        shutil.copy(os.path.join(CARDS, f), os.path.join(SITE, f))
    for extra in ("latest.md",):
        p = os.path.join(CARDS, extra)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(SITE, extra))

    rows = "\n".join('<li><a href="{}">{}</a></li>'.format(f, f[:-5]) for f in files)
    latest = files[-1][:-5] if files else ""

    tail = (
        '<div class="card">\n'
        '<p><strong>{hook}</strong></p>\n'
        '<p>最新一条：<a href="{latest}.html">{latest}</a></p>\n'
        '<p>推翻入口：<code>{refute}</code><br>\n'
        '只补一个源也可以（30 秒）：<code>{source}</code></p>\n'
        '</div>\n'
        '<div class="foot">本站点由纯脚本生成，推送即更新，不调用任何生成式模型。<br>\n'
        '觉思者 Juesizhe · MIT License</div>\n'
        '</body></html>\n'
    ).format(hook=HOOK, latest=latest, refute=REFUTE, source=SOURCE)

    page = PAGE_HEAD + PAGE_MID.format(rows=rows) + tail
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as fp:
        fp.write(page)
    print("OK _site/index.html（共 {} 张卡片）".format(len(files)))


if __name__ == "__main__":
    main()
