#!/usr/bin/env python3
"""CJK 汉字字数计数器 + 「A-B 字」预算门。

用途：用户给出「写成 1200-1800 字」这类**字数**硬区间时（区别于**行数**区间——
行数压缩走 scripts/md_trim_report.py，它只删空行，对字数几乎没有作用），
写完立刻核对，避免首稿超限后整篇返工。

用法：
    python cjk_wc.py <file.md>                        # 仅统计
    python cjk_wc.py <file.md> --min 1200 --max 1800  # 附预算判定

统计口径：
    han        纯汉字（\\u4e00-\\u9fff）—— 本 skill 报「字数」时以此为主口径（LULU 2026-11 实测）
    han_punct  汉字 + 中文标点（更接近 Word/WPS「字数」的偏大读数，约 +10~15%）
    latin      英文单词数（品牌名/ticker 各算 1）
    table      表格行数 —— 压缩时禁止动的部分

退出码：0 = 在区间内；1 = 超上限；2 = 低于下限；3 = 未给预算（仅统计）
"""
import argparse
import re
import sys

HAN = re.compile(r'[\u4e00-\u9fff]')
HAN_PUNCT = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')
LATIN_WORD = re.compile(r'[A-Za-z][A-Za-z0-9.\-]*')


def stats(path):
    text = open(path, encoding='utf-8').read()
    lines = text.splitlines()
    table_rows = sum(1 for ln in lines if ln.lstrip().startswith('|'))
    return {
        'han': len(HAN.findall(text)),
        'han_punct': len(HAN_PUNCT.findall(text)),
        'latin': len(LATIN_WORD.findall(text)),
        'table': table_rows,
        'lines': len(lines),
        'chars': len(text),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--min', type=int, default=None)
    ap.add_argument('--max', type=int, default=None)
    args = ap.parse_args()

    s = stats(args.file)
    print('file      : %s' % args.file)
    print('汉字       : %d   (报告「字数」主口径)' % s['han'])
    print('汉字+标点  : %d' % s['han_punct'])
    print('英文词     : %d' % s['latin'])
    print('表格行     : %d   (压缩时保留)' % s['table'])
    print('行数       : %d  总字符: %d' % (s['lines'], s['chars']))

    if args.min is None and args.max is None:
        return 3
    n = s['han']
    if args.max is not None and n > args.max:
        print('判定       : OVER  —— 超上限 %d 字；压缩论证性散文，表格与数字一律保留' % (n - args.max))
        return 1
    if args.min is not None and n < args.min:
        print('判定       : UNDER —— 差 %d 字；补机制/证据段落，不要灌水' % (args.min - n))
        return 2
    print('判定       : OK    —— 处于 %s~%s 区间' % (args.min or '-', args.max or '-'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
