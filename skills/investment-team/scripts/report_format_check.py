#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文子报告的「格式契约」校验器（investment-team 单文件模式专用）。

用途：用户用「字数」而非「行数」给篇幅时（如「1200-1800 字」「结尾单起一行」「段落之间不留空行」），
写完必须机器复核，不靠肉眼。行数契约仍用 scripts/md_trim_report.py。

用法：
    python3 report_format_check.py <file.md>
    python3 report_format_check.py <file.md> --min-cn 1200 --max-cn 1800 --min-tables 3
    python3 report_format_check.py <file.md> --end-line "投资吸引力评分："

自检项：
  1) 中文字符数（仅统计 \\u4e00-\\u9fff；中英混排的美元/百分比不计入，与用户「X 字」的口径一致）
  2) Markdown 表格数量（`|---` 分隔行计数，即表格个数）
  3) 段落间空行（正文→正文之间出现空行即违规；标题前后、表格前后、引用块之间的空行合法）
  4) 结尾最后一行是否为目标句式（如「投资吸引力评分：X.XX/5（…）」）
  5) 标题清单（便于核对章节数是否与契约一致）

退出码：有 hard fail 返回 1，否则 0。

⚠️ 实战教训（LULU 2026-11）：
  - 不要用 `terminal(python3 -c "...多行含 \\u 转义的正则...")` 做这件事——内联多行 Python + CJK 正则
    在本机会整条命令超时被 BLOCK。正确姿势：write_file 落一个 .py，再 `terminal(python3 /tmp/x.py)`。
  - 文件末尾的单个换行会让「正文→空行」检测在第 N+3 行误报一次，属正常（本脚本已排除 EOF）。
  - 「段落之间不留空行」是有意为之的排版：相邻两段会被 Markdown 渲染成同一段（视觉上以空格相连）。
    这是用户要求，不是 bug，不要「为了好看」加回空行。
"""
import argparse
import re
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--min-cn", type=int, default=0)
    ap.add_argument("--max-cn", type=int, default=10**9)
    ap.add_argument("--min-tables", type=int, default=0)
    ap.add_argument("--end-line", default=None, help="结尾最后一行须以此开头")
    a = ap.parse_args()

    text = open(a.path, encoding="utf-8").read()
    cn = len(re.findall(r"[\u4e00-\u9fff]", text))
    lines = text.split("\n")
    tables = sum(1 for l in lines if l.startswith("|") and "---" in l)
    heads = [l for l in lines if l.startswith("#")]
    last = next((l for l in reversed(lines) if l.strip()), "")

    fails, warns = [], []

    # 1) 中文字符数
    status = "OK" if a.min_cn <= cn <= a.max_cn else "FAIL"
    if status == "FAIL":
        fails.append(f"中文字符 {cn} 不在 [{a.min_cn}, {a.max_cn}]")
    print(f"[{status}] 中文字符 {cn}（区间 {a.min_cn}-{a.max_cn}）")

    # 2) 表格数
    status = "OK" if tables >= a.min_tables else "FAIL"
    if status == "FAIL":
        fails.append(f"表格 {tables} < 必需 {a.min_tables}")
    print(f"[{status}] 表格数 {tables}（至少 {a.min_tables}）")

    # 3) 正文段间空行（排除 EOF 的尾部空行）
    bad = []
    for i, l in enumerate(lines):
        if not l.strip():
            prev = lines[i - 1] if i > 0 else ""
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if prev.strip() and nxt.strip() and not prev.startswith(("#", "|", ">")) \
                    and not nxt.startswith(("#", "|", ">")):
                bad.append(i + 1)
    if bad:
        warns.append(f"正文段间疑似空行：行 {bad}（若确为用户不要空行的契约 → 删掉）")
        print(f"[WARN] 正文段间空行 {len(bad)} 处：行 {bad}")
    else:
        print("[OK] 正文段间无空行")

    # 4) 结尾句式
    if a.end_line:
        ok = last.startswith(a.end_line)
        print(f"[{'OK' if ok else 'FAIL'}] 结尾行：{last[:60]!r}")
        if not ok:
            fails.append(f"结尾最后一行不以「{a.end_line}」开头")
        if len(last) > 200:
            warns.append("结尾行过长——应为单行短句，评分与口径同处一行")

    print(f"\n标题 {len(heads)} 个：")
    for h in heads:
        print("  " + h[:70])

    for w in warns:
        print("[WARN] " + w)
    for f in fails:
        print("[FAIL] " + f)
    print("\n结论：" + ("通过" if not fails else "未通过，需修复后再交付"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
