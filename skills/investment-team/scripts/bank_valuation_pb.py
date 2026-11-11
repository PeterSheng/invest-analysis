#!/usr/bin/env python3
"""Bank P/B valuation stack (ROTE -> P/B Gordon form, reverse-solve implied ROTE, sensitivity grid).

Why this script: for banks the valuation anchor is P/B driven by sustainable ROTE vs COE,
NOT DCF/FCF. Hand-building three tables every bank report is error-prone; this prints the
exact markdown tables to paste into 02-财务估值-巴菲特视角.md.

Formulas
  fair_pb(rote, coe, g)      = (ROTE - g) / (COE - g)      # Gordon growth, g in perpetuity
  implied_rote(pb, coe, g)   = pb*(COE - g) + g            # reverse-engineer what the market believes
  fair_price                 = fair_pb * BVPS              # use COMMON-equity BVPS, never total equity

Usage
  python bank_valuation_pb.py --bvps 79.47 --tbvps 73.90 --price 137.50 \
      --rote 13,15.5,17.5 --coe 10.5 --g 3.5 \
      --grid-coe 9.5,10.5,11.0 --grid-rote 13,15,17,19 \
      --divps 6.1

Notes
  * BVPS must EXCLUDE AT1 / preferred / minority interests (see references §10).
  * Quote-provider PB (Tencent / stockanalysis) usually divides by total equity incl. AT1
    -> systematically understates P/B by 10-20 bps... actually 0.1-0.3 turns. Always self-compute.
  * Pass --divps to get the DPS-inclusive holding return (retained BVPS growth + dividend yield).
"""
import argparse
from typing import List


def _floats(s: str) -> List[float]:
    return [float(x) for x in s.split(",") if x.strip()]


def fair_pb(rote_pct: float, coe_pct: float, g_pct: float) -> float:
    if coe_pct <= g_pct:
        raise ValueError("COE must exceed g")
    return (rote_pct - g_pct) / (coe_pct - g_pct)


def implied_rote(pb: float, coe_pct: float, g_pct: float) -> float:
    return pb * (coe_pct - g_pct) + g_pct


def fmt(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bvps", type=float, required=True, help="common-equity BVPS")
    p.add_argument("--tbvps", type=float, default=None)
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--rote", type=float, nargs="+", default=[13.0, 15.5, 17.5],
                   help="ROTE scenarios in %% (space or comma separated)")
    p.add_argument("--coe", type=float, default=10.5)
    p.add_argument("--g", type=float, default=3.5)
    p.add_argument("--grid-coe", type=_floats, default=[9.5, 10.5, 11.0])
    p.add_argument("--grid-rote", type=_floats, default=[13.0, 15.0, 17.0, 19.0])
    p.add_argument("--divps", type=float, default=None)
    a = p.parse_args()

    pb_now = a.price / a.bvps
    print(f"## 现价锚\n\n现价 {a.price} / BVPS {a.bvps} = **P/B {fmt(pb_now)}x**")
    if a.tbvps:
        print(f"现价 / TBVPS {a.tbvps} = **P/TBV {fmt(a.price / a.tbvps)}x**"
              f"（BV/TBV 差 {fmt((a.bvps / a.tbvps - 1) * 100, 1)}% = 商誉+无形资产占比）")
    print(f"\n**现价隐含可持续 ROTE = {fmt(implied_rote(pb_now, a.coe, a.g), 2)}%**"
          f"（COE {a.coe}% / g {a.g}%）——市场已经相信的回报率，逐条对照公司披露与同业。\n")

    print("## 表一：ROTE 情景 → 公允 P/B → 公允价\n")
    print(f"| ROTE | 公允 P/B (COE {a.coe}% / g {a.g}%) | 公允价 | vs 现价 |")
    print("|---:|:---:|---:|:---:|")
    for r in a.rote:
        fpb = fair_pb(r, a.coe, a.g)
        fp = fpb * a.bvps
        print(f"| {fmt(r, 1)}% | {fmt(fpb)}x | {fmt(fp)} | {(fp / a.price - 1) * 100:+.1f}% |")

    print("\n## 表二：COE × ROTE 敏感性（公允 P/B）\n")
    header = "| ROTE \\ COE | " + " | ".join(f"{fmt(c, 1)}%" for c in a.grid_coe) + " |"
    print(header)
    print("|---|" + "---:|" * len(a.grid_coe))
    for r in a.grid_rote:
        cells = []
        for c in a.grid_coe:
            fpb = fair_pb(r, c, a.g)
            cells.append(f"{fmt(fpb)}x / {fmt(fpb * a.bvps)}")
        print(f"| **{fmt(r, 1)}%** | " + " | ".join(cells) + " |")
    print("\n_每格 = 公允 P/B / 公允价（基于 BVPS " + fmt(a.bvps) + "）_\n")

    if a.divps:
        print("## 表三：持有期回报拆解（exit P/B 不变）\n")
        for r in a.rote:
            payout = a.divps / (a.bvps * r / 100) if a.bvps * r else 0.0
            ret_bv = r / 100 * (1 - payout)
            dy = a.divps / a.price
            print(f"- ROTE {fmt(r, 1)}% ：payout {fmt(payout * 100, 0)}% "
                  f"-> 留存复利 {fmt(ret_bv * 100, 1)}% + 股息率 {fmt(dy * 100, 1)}% "
                  f"= **年化约 {fmt((ret_bv + dy) * 100, 1)}%**"
                  f"（再乘上 ex-ante 的 P/B 重估系数）")
        print("")


if __name__ == "__main__":
    main()
