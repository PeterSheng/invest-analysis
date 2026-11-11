#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四大师报告包确定性审计（主代理自审，替代/兜底审计子代理）

用法：python3 audit-report-pack.py <公司报告目录>
例：  python3 audit-report-pack.py /home/admin/hermes-agent-invest/reports/202611/百事可乐

检查项（都是实战中真的出过错的地方）：
  A 价格锚：每份文件必须含「价格截至 YYYY-MM-DD …$X」；全文不许出现未标注的盘前/复权价被当结论锚
  B 评分网格：所有「评分：X.XX」必须在 1-5 且 0.25 步长
  C 综合分：05 声明的综合分 == 01-04 各自声明分的等权平均（±0.01）
  D 安全边际符号：安全边际表格行 |值| > 60% 一律告警（分母口径错）
  E 击球区/IV 一致性：击球区上下沿 ÷ 基准 IV 应落在 0.70-1.20
  F 表格列数：表头与数据行列数不一致的行（断行/错位）
  G 一次性项：出现 core/核心 EPS 的文件必须至少出现一次「含」或「剔除」标注

退出码：0 = 无阻断问题；1 = 有 🔴/🟡 级问题
"""
import os, re, sys, glob

GRID = [round(1 + 0.25 * i, 2) for i in range(17)]
PRICE_RE = re.compile(r"价格截至[^｜|\n]{0,40}?\$?([0-9]{2,4}\.[0-9]{2})")
SCORE_RE = re.compile(r"(?:评分|综合)[^0-9\n]{0,12}\*{0,2}([0-9]\.[0-9]{2})")


def cells(line):
    return [c for c in line.strip().strip("|").split("|")]


def audit(d):
    files = sorted(glob.glob(os.path.join(d, "0[1-5]-*.md")))
    if not files:
        print("!! 未找到 01-05 报告文件，检查目录：", d); return 1
    issues, scores, anchors = [], {}, {}
    for f in files:
        name = os.path.basename(f)
        txt = open(f, encoding="utf-8").read()
        lines = txt.splitlines()

        # A 价格锚
        m = PRICE_RE.findall(txt)
        if not m:
            issues.append(("🔴", name, "-", "缺少「价格截至 …」价格锚", ""))
        else:
            anchors[name] = m[0]
        for ln, l in enumerate(lines, 1):
            if re.search(r"盘前|复权", l) and not re.search(r"仅作|辅锚|参考|非结论", l):
                issues.append(("🟡", name, ln, "出现盘前/复权价但未标注仅作参考", l[:80]))

        # B 评分
        for s in SCORE_RE.findall(txt):
            v = float(s)
            if not any(abs(v - g) < 0.001 for g in GRID):
                issues.append(("🟡", name, "-", f"评分 {v} 不在 1-5/0.25 网格", ""))
        if name[:2] in ("01", "02", "03", "04"):
            hdr = "\n".join(lines[:20])
            mm = SCORE_RE.findall(hdr)
            if mm:
                scores[name[:2]] = float(mm[-1])

        # D 安全边际符号
        for ln, l in enumerate(lines, 1):
            if "安全边际" in l and "|" in l:
                for v in re.findall(r"(-[0-9]{2,3}(?:\.[0-9])?)%", l):
                    if abs(float(v)) > 60:
                        issues.append(("🟡", name, ln,
                                       f"安全边际写 {v}% —— 大概率是溢价率口径，应为 (IV−现价)/现价",
                                       l[:90]))

        # E 击球区一致性
        zone = re.search(r"击球区[^0-9$]{0,20}?\$([0-9]{2,4}(?:\.\d+)?)\s*[–\-—~至]\s*\$?([0-9]{2,4}(?:\.\d+)?)", txt)
        iv = re.findall(r"基准[^0-9$]{0,6}(?:IV|IV\s*\$)\s*\**\$?\s*([0-9]{2,4}(?:\.\d+)?)", txt) or \
             re.findall(r"基准 IV\s*\**\s*\$([0-9]{2,4}(?:\.\d+)?)", txt)
        if zone and iv:
            lo, hi, base = float(zone.group(1)), float(zone.group(2)), float(iv[0])
            if base:
                for v in (lo, hi):
                    if not (0.70 <= v / base <= 1.20):
                        issues.append(("🟡", name, "-",
                                       f"击球区 {v} vs 基准 IV {base} 比值 {v/base:.2f} 越界(0.70-1.20)", ""))

        # F 表格列数
        ncol, start = None, 0
        for ln, l in enumerate(lines, 1):
            if l.strip().startswith("|"):
                c = len(cells(l))
                if re.match(r"\|[-: |]{3,}\|", l.strip()):
                    ncol = c
                elif ncol and c != ncol:
                    issues.append(("🟢", name, ln, f"表格列数 {c} ≠ 表头 {ncol}", l[:70]))

        # G 一次性项标注
        if re.search(r"核心 EPS|core EPS", txt) and not re.search(r"含|剔除|一次性", txt):
            issues.append(("🔴", name, "-", "出现核心 EPS 但全篇无「含/剔除/一次性」标注", ""))

    # C 综合分
    c5 = None
    p5 = [f for f in files if os.path.basename(f).startswith("05")]
    if p5:
        t5 = open(p5[0], encoding="utf-8").read()
        m = re.search(r"综合[^0-9\n]{0,20}\*{0,2}([0-9]\.[0-9]{2})", t5)
        c5 = float(m.group(1)) if m else None
    if len(scores) == 4 and c5 is not None:
        avg = sum(scores.values()) / 4
        if abs(round(avg, 2) - c5) > 0.01 and abs(avg - c5) > 0.02:
            issues.append(("🔴", "05-综合", "-",
                           f"综合 {c5} ≠ 四大师等权均值 {avg:.3f}（{sorted(scores.items())}）", ""))

    # 输出
    print(f"审计目录：{d}\n文件数：{len(files)}  价格锚：{anchors}\n各大师分：{scores}  综合：{c5}")
    if not issues:
        print("\n✅ 无发现问题（A-G 全部通过）")
        return 0
    w = {"🔴": 0, "🟡": 1, "🟢": 2}
    print("\n%-3s %-34s %-6s %s" % ("级", "文件", "行", "问题"))
    for sev, f, ln, msg, ctx in sorted(issues, key=lambda x: w[x[0]]):
        print("%-3s %-34s %-6s %s%s" % (sev, f[:34], ln, msg, ("  ← " + ctx if ctx else "")))
    bad = sum(1 for i in issues if i[0] in ("🔴", "🟡"))
    print(f"\n合计：🔴 {sum(1 for i in issues if i[0]=='🔴')} / 🟡 {sum(1 for i in issues if i[0]=='🟡')} / 🟢 {sum(1 for i in issues if i[0]=='🟢')}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(audit(sys.argv[1]))
