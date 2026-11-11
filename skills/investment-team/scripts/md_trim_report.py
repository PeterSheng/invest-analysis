#!/usr/bin/env python3
"""md_trim_report.py — 把长 Markdown 报告压进行数预算，并给出「还需删几行内容」的精确提示。

背景（港交所 2026-11 实战教训）：子报告要求 160-280 行，初稿写成 356 行，
之后用 6 次零散正则清理才压到 280 行，其中两次脚本写错（忘记写盘 / 用错的匹配键），
还删掉了必含表格的行（三情景表拆项、DDM 9.5% 行），事后还得靠人眼回读验证。

正确做法：先跑本脚本（默认 dry-run），再决定删哪几行内容。

压缩顺序（只做这三件事，绝不为了行数牺牲表格）：
  1. 删除「后接标题」的空行            (# / ## / ###)
  2. 删除「前接 ---」的空行            （分隔线后的空行）
  3. 删除「正文紧接正文」之间的空行    （两段都非表格行、非列表行、非引用行）

保留：标题后的空行、表格前后空行、列表/引用块之间的空行、表格后的空行（渲染必需）。

用法：
    python3 md_trim_report.py <file.md>                  # dry-run，只报告
    python3 md_trim_report.py <file.md> --apply          # 实际写盘
    python3 md_trim_report.py <file.md> --max 280 --apply  # 压完后仍超则提示还需删几行
"""
import sys
import re


def is_table_row(s: str) -> bool:
    return s.lstrip().startswith('|')


def is_block_start(s: str) -> bool:
    """列表 / 引用 / 代码块 / 表格 —— 这些块的边界空行要保留。"""
    t = s.lstrip()
    return t.startswith(('|', '-', '*', '+', '>', '```', '1.', '2.', '3.')) or bool(re.match(r'\d+\.', t))


def compact(lines):
    out = []
    for i, line in enumerate(lines):
        if line.strip() == '' and i + 1 < len(lines):
            nxt = lines[i + 1].lstrip()
            prev = out[-1].strip() if out else ''
            # 规则 1：后接标题
            if nxt.startswith('#'):
                continue
            # 规则 2：前接分隔线
            if prev == '---':
                continue
            # 规则 3：正文接正文（两侧都不是表格/列表/引用/代码块）
            if prev and not is_table_row(prev) and not is_table_row(nxt) \
                    and not is_block_start(prev) and not is_block_start(nxt) \
                    and prev != '---':
                continue
        # 折叠连续空行为一行
        if line.strip() == '' and out and out[-1].strip() == '':
            continue
        out.append(line)
    return out


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__)
        return 1
    path = args[0]
    apply = '--apply' in args
    max_lines = None
    if '--max' in args:
        max_lines = int(args[args.index('--max') + 1])

    raw = open(path, encoding='utf-8').read().split('\n')
    if raw and raw[-1] == '':
        raw = raw[:-1]
    new = compact(raw)
    text = '\n'.join(new).rstrip('\n') + '\n'

    print(f'{path}: {len(raw)} -> {len(new)} 行 (省 {len(raw) - len(new)} 行)')

    if max_lines and len(new) > max_lines:
        over = len(new) - max_lines
        print(f'⚠ 仍超预算 {over} 行（目标 ≤{max_lines}）')
        print('可删的候选（次要表行 —— 删前确认信息在正文里还有，且不得动三情景/敏感性/同业对比三张必含表）：')
        mandatory = ('情景', '悲观', '基准', '乐观', 'WACC', ' tg ', 'r \\', 'PE 20x', 'PE 25x', 'PE 28x', 'HKEX', 'CME', '同业中位')
        cand = 0
        for ln in new:
            if is_table_row(ln) and '---' not in ln:
                if not any(k in ln for k in mandatory):
                    cand += 1
                    if cand <= over + 3:
                        print('   ', ln.strip()[:100])
        print(f'   共 {cand} 行非必含表行可选')
    if apply:
        open(path, 'w', encoding='utf-8').write(text)
        print('已写盘')
    else:
        print('（dry-run，加 --apply 写盘）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
