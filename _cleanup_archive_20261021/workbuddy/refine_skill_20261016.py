# -*- coding: utf-8 -*-
"""2026-10-16 夜间汇总精炼：仅改 SKILL.md 的 AUTO_EVOLVE 标记区间。"""
import io, sys, re

p = 'SKILL.md'
with open(p, encoding='utf-8', newline='') as f:
    txt = f.read()

nl = '\r\n' if '\r\n' in txt else '\n'
lines = txt.split(nl)
i0 = next(i for i, l in enumerate(lines) if l.strip() == '<!-- AUTO_EVOLVE_START -->')
i1 = next(i for i, l in enumerate(lines) if l.strip() == '<!-- AUTO_EVOLVE_END -->')
print('block', i0 + 1, i1 + 1)

def sub_line(idx, old, new, cnt=1):
    l = lines[idx]
    if l.count(old) < cnt:
        print('!! MISS line', idx + 1, old[:60]); sys.exit(1)
    lines[idx] = l.replace(old, new, cnt)
    print('ok line', idx + 1, '|', old[:40], '->', new[:40])

# A. P4 索引 二十二 -> 二十八
sub_line(60,
    '㉒冲突的结算通道（由哪条通道结算、是否双向可入且对等可执行、攻击的收益与代价是否同归一个主体，P29）。',
    '㉒冲突的结算通道（由哪条通道结算、是否双向可入且对等可执行、攻击的收益与代价是否同归一个主体，P29）'
    '㉓退出权的归属——谁买得起「不参与」（P30）㉔预告的归属与回灌方向（P31）㉕分节的归属——谁来切分这一段、切分依据可否被更新（P32）'
    '㉖规则与酬赏的归属侧（在玩 / 被玩之分界，P33）㉗身后版本的托管权与终结权（P34）㉘腾出位置的接管权与回写权（P35）。')
sub_line(60, '已析出的可编辑项二十二类', '已析出的可编辑项二十八类')

# B/C/D. 删「序链已由夜间汇总精炼归一」类过程留痕
sub_line(72, '，与前九项并列不冲突（序链已由夜间汇总精炼归一）', '，与前九项并列不冲突')
sub_line(77, '，与前十三项并列不冲突（序链已由夜间汇总精炼归一至十六项）', '，与前十三项并列不冲突')
sub_line(78, '（谁替不能自陈者说话，并能叫停）（序链已由夜间汇总精炼归一至十六项）', '（谁替不能自陈者说话，并能叫停）')

# E. P30 删「交由夜间汇总精炼统一处理」过程留痕（本轮已办）
sub_line(86, '）**（跨条目索引的同步更新交由「夜间汇总精炼」统一处理）。**点化**',
             '）。**点化**')

# F. P31 删已由 P4 索引承载的互注
sub_line(87, '方向**（第二十三项「退出权的归属」见 P30）。**划界**', '方向。**划界**')

# G. P33 删本机缺陷过程留痕（完整留痕已存于 PHILOSOPHY.md 自我改进日志）
sub_line(89, '②**儒**（编排者补入，本机两轮均未给儒、佛条目）：', '②**儒**：')
sub_line(89, '③**佛**（编排者补入，本机两轮均未给儒、佛条目）：', '③**佛**：')
sub_line(89, '④**诸子**（编排者补入墨、名、兵，本机只给了荀）：', '④**诸子**：')

# H. 年份标注体例统一：删除「不得伪称 2026 / 非 2026」式口令（年份已写在出处中）
for idx in range(i0, i1):
    l = lines[idx]
    if '不得伪称 2026' in l or '，非 2026）' in l:
        new = l.replace('，如实标注为 2025，不得伪称 2026', '，如实标注 2025') \
               .replace('**如实标注为 2025，不得伪称 2026**', '**如实标注 2025**') \
               .replace('，如实标注为 2024，不得伪称 2026', '，如实标注 2024') \
               .replace('**如实标注为 2024，不得伪称 2026**', '**如实标注 2024**') \
               .replace('（**年份如实标注 2025**，非 2026）', '（**如实标注 2025**）')
        if new != l:
            lines[idx] = new
            print('ok year-norm line', idx + 1)

out = nl.join(lines)
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(out)

# 核验
chk = open(p, encoding='utf-8', newline='').read()
L = chk.split(nl)
a = next(i for i, l in enumerate(L) if l.strip() == '<!-- AUTO_EVOLVE_START -->')
b = next(i for i, l in enumerate(L) if l.strip() == '<!-- AUTO_EVOLVE_END -->')
ids = re.findall(r'^- (P\d+) ', '\n'.join(L[a + 1:b]), re.M)
print('block', a + 1, b + 1, 'entries', len(ids))
print('ids', ','.join(ids))
print('可编辑项二十八类 present:', '可编辑项二十八类' in '\n'.join(L[a + 1:b]))
