# -*- coding: utf-8 -*-
"""CORE.md 域归属体检（五查）——只读，不写盘。

用法：python scripts/check_core_domains.py

查①  来源映射抬头「命题库 X 条 / 纲要共 X 条」是否与权威计数一致
查②  条目物理所在域 vs 域标题括号声明（错位 / 未收录）
查③  条目是否被误置在「分工说明」正文区或纲要区之外
查④  域标题清单 vs 分工说明域名清单（含**整行缺失**——历轮最易漏的一类）
查⑤  来源映射逐条映射行最大 Cn vs 纲要最大 Cn（只查抬头数查不出缺行）

坑（2026-10-25 实测）：
  * 分工说明行的枚举末尾带 `**`（如 `…、C78**：…`），expand 前须 strip('*')；
  * 「骨干」不带「域」字，正则须并列 `(域|骨干)` 且允许域名为空前缀；
  * 心律段 `- **新增N问的共同心律与分工（Cxx–Cyy）**：` 也以 `- **` 起头，
    须以「域名后紧跟 Cn 枚举」区分，否则会被误当成域行。
"""
import re
import sys

EOL = '\r\n'
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core_source  # noqa: E402  2026-10-27 起 CORE.md 按域分册，统一经加载器取逻辑整文档

CORE = 'CORE.md'


def rd(p=None):
    """返回逻辑整文档的行列表（CORE.md + 七卷拼回原位）。"""
    return core_source.lines()


def expand(spec):
    out = set()
    for part in re.split(r'[、,，]', spec):
        part = part.strip().strip('*').strip()
        if not part:
            continue
        m = re.match(r'^C(\d+)\s*[–\-~]\s*C(\d+)$', part)
        if m:
            out |= set(range(int(m.group(1)), int(m.group(2)) + 1))
            continue
        m = re.match(r'^C(\d+)$', part)
        if m:
            out.add(int(m.group(1)))
    return out


def main():
    C = rd()
    entry_i = next(i for i, l in enumerate(C) if l.startswith('## 核心纲要'))
    work_i = next(i for i, l in enumerate(C) if l.startswith('## 分工说明'))
    map_i = next(i for i, l in enumerate(C) if l.startswith('## 来源映射'))

    # 物理域
    phys, cur = {}, None
    for i, l in enumerate(C):
        if l.startswith('### '):
            m = re.match(r'^### (.+?)（', l)
            cur = m.group(1).strip() if m else l[4:].strip()
        m = re.match(r'^- \*\*C(\d+)', l)
        if m and entry_i < i < work_i:
            phys[int(m.group(1))] = cur

    # 域标题声明
    title, order = {}, []
    for l in C:
        m = re.match(r'^### (.+?)（(.+?)）', l)
        if m:
            title[m.group(1).strip()] = expand(m.group(2))
            order.append(m.group(1).strip())

    # 分工说明域行（域名 + 紧随的 Cn 枚举）
    work = {}
    for l in C[work_i:map_i]:
        m = re.match(r'^- \*\*(.*?)(域|骨干)\s+(C[^：]*?)：', l)
        if m:
            work[(m.group(1) + m.group(2)).strip()] = expand(m.group(3))

    maxC = max(phys) if phys else 0
    print('== 纲要条目 ==')
    print('  条目数 %d / 最大 Cn %d / 缺号 %s'
          % (len(phys), maxC, [n for n in range(1, maxC + 1) if n not in phys]))

    print('\n== 查② 物理域 vs 域标题声明 ==')
    rev = {}
    for d, s in title.items():
        for n in s:
            rev.setdefault(n, []).append(d)
    bad = [(n, phys[n], rev.get(n, [])) for n in sorted(phys) if phys[n] not in rev.get(n, [])]
    for n, p, ds in bad:
        print('  错位: C%d 在[%s]，标题声明%s' % (n, p, ds))
    print('  错位 %d / 未被任何域标题收录 %s'
          % (len(bad), [n for n in sorted(phys) if not rev.get(n)]))

    print('\n== 查③ 误置条目（纲要区之外） ==')
    stray = [(i + 1, l[:50]) for i, l in enumerate(C)
             if re.match(r'^- \*\*C\d+', l) and not (entry_i < i < work_i)]
    for a, b in stray:
        print('  line%d %s' % (a, b))
    print('  误置 %d' % len(stray))

    print('\n== 查④ 域标题清单 vs 分工说明域行 ==')
    for d in order:
        t, w = title[d], work.get(d)
        if w is None:
            print('  【整行缺失】域[%s] 在分工说明区无对应行（%d 条无分工说明）' % (d, len(t)))
        elif t != w:
            print('  域[%s] 标题-only %s / 分工-only %s' % (d, sorted(t - w), sorted(w - t)))
    print('  分工说明已覆盖域: %s' % sorted(work.keys()))

    print('\n== 查①⑤ 来源映射 ==')
    head = [l for l in C[map_i:map_i + 4] if l.startswith('>')][:2]
    for l in head:
        nums = [int(x) for x in re.findall(r'\*\*(\d+) 条\*\*', l)]
        print('  抬头: %s… → 计数 %s' % (l[:60], nums))
    maps = {}
    for l in C[map_i:]:
        for m in re.finditer(r'C(\d+)\s*←\s*P(\d+)', l):
            maps[int(m.group(1))] = int(m.group(2))
    print('  映射行 %d / 最大 Cn %d / 缺映射 %s'
          % (len(maps), max(maps) if maps else 0,
             [n for n in range(1, maxC + 1) if n not in maps]))

    print('\n== 计数四处 ==')
    for i, l in enumerate(C):
        for m in re.finditer(r'可编辑[者项]*\s*[〇一二三四五六七八九十百]+(类|项)?', l):
            print('  line%d: %s' % (i + 1, m.group(0)))


if __name__ == '__main__':
    main()
