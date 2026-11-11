"""生成芒格风险子报告的「统一灵敏度表 + 双杀矩阵」

用途：在写 03-风险分析-芒格视角.md 之前跑一次，把"一根杠杆、三个后果"钉死，
之后所有失败路径的影响量化都从这张表取数，避免九条路径各用一套口径。

用法：
    python risk_sensitivity.py            # 跑内置 PEP 2026-11 示例
    from risk_sensitivity import build   # 或 import 后传自己的字典

设计纪律：
  - 现倍数 × 现 EPS 必须 ≈ 现价（否则倍数口径 core/GAAP/TTM/FWD 混用了，先修口径）
  - 每 $1B 税前营业利润 → EPS / FCF / 股息覆盖 / 净债EBITDA 四条后果一次算完
  - 双杀矩阵的读法固定为"单杀可忍 / 双杀致命 / 盯倍数而非盯 EPS"
"""

from __future__ import annotations


def build(base: dict) -> dict:
    """base 键说明（单位：billion USD / million shares / USD per share）

    eps        核心 EPS（剔一次性后优先）
    shares_m   稀释股本（百万股）
    tax        有效税率（0.24 = 24%）
    conv       净利 → 正常化 FCF 转换系数（0.68 = 68%）
    fcf_b      正常化 FCF（十亿美元）
    div_b      股息总额（十亿美元）
    ebitda_b   EBITDA
    netdebt_b  净债务
    price      现价
    multiple   现价对应的核心 PE
    """
    eps = base["eps"]
    shares = base["shares_m"]
    tax, conv = base["tax"], base["conv"]

    # ---- 自校验门：倍数与 EPS 必须能还原现价 ----
    implied_price = base["multiple"] * eps
    price = base["price"]
    drift = abs(implied_price / price - 1)
    recon_ok = drift < 0.005

    # ---- 一根杠杆：$1B 税前核心营业利润的三层后果 ----
    per_b_net = 1000 * (1 - tax)                      # $M 净利
    per_b_eps = per_b_net / shares                    # $/股
    per_b_fcf = (1 - tax) * conv                      # $B FCF
    per_b_cov = per_b_fcf / base["div_b"]             # 股息覆盖倍数变化
    per_b_lev = (1 - tax) / base["ebitda_b"] * 1000   # 净债/EBITDA 变化(x) —— 反号
    lever = {
        "税前 $1B": 1.0,
        "净利 $B": round(per_b_net / 1000, 3),
        "EPS $/股": round(per_b_eps, 2),
        "EPS 占当前 %": round(per_b_eps / eps * 100, 1),
        "FCF $B": round(per_b_fcf, 2),
        "股息覆盖 (x)": round(-per_b_cov, 3),
        "净债/EBITDA (x)": round(per_b_lev, 2),
    }

    # ---- 当期体检 ----
    coverage = base["fcf_b"] / base["div_b"]
    lev_now = base["netdebt_b"] / base["ebitda_b"]

    # ---- 双杀矩阵：EPS 情景 × 倍数情景 ----
    eps_paths = [round(eps * f, 2) for f in (1.00, 0.975, 0.933, 0.90, 0.867)]
    mults = [12, 13, 14, 15, round(base["multiple"], 1)]
    matrix = {f"EPS ${e:.2f}": {f"{m}x": round(e * m, 0) for m in mults} for e in eps_paths}

    # ---- 分部单点换算：年化收入 × 利润率 bp 变动 ----
    def segment(rev_b: float, bp: int) -> dict:
        pre = rev_b * bp / 10000 * 1000            # $M 税前
        after = pre * (1 - tax)
        return {"收入 $B": rev_b, "变动 bp": bp,
                "税前 $M": round(pre, 0),
                "EPS 影响 $": round(after / shares, 2),
                "占 EPS %": round(after / shares / eps * 100, 1)}

    return {
        "recon": {"现倍数 × EPS": round(implied_price, 2), "现价": price,
                  "偏差 %": round(drift * 100, 2), "口径自洽": recon_ok},
        "lever": lever,
        "coverage_x": round(coverage, 2),
        "netdebt_ebitda_x": round(lev_now, 2),
        "matrix": matrix,
        "mult_cols": mults,
        "segment_100bp": segment(26.5, 100),   # PEP PFNA 年化 ~$265 亿
    }


def render(r: dict) -> str:
    out = []
    recon = r["recon"]
    out.append(f"【口径自洽门】 {recon['现倍数 × EPS']} vs 现价 {recon['现价']}"
               f"  → 偏差 {recon['偏差 %']}%  自洽={recon['口径自洽']}")

    if not r["recon"]["口径自洽"]:
        out.append("  ⚠️ 倍数口径不自洽（core/GAAP 或 TTM/FWD 混用），先修口径再写报告")

    out.append("\n【统一灵敏度表】每 $1B 税前核心营业利润 →")
    for k, v in r["lever"].items():
        out.append(f"  {k:<16} {v}")

    out.append("\n【当期体检】")
    out.append(f"  股息覆盖      {r['coverage_x']}x   (<1.0 = 用债务付股息)")
    out.append(f"  净债/EBITDA   {r['netdebt_ebitda_x']}x")

    out.append("\n【双杀矩阵】EPS × 倍数（$/股）")
    cols = r["mult_cols"]
    out.append("  " + "| EPS".ljust(14) + "".join(f"| {m}x".rjust(9) for m in cols))
    for eps_lbl, row in r["matrix"].items():
        out.append("  " + f"| {eps_lbl}".ljust(14)
                   + "".join(f"| {int(row[f'{m}x'])}".rjust(9) for m in cols))

    seg = r["segment_100bp"]
    out.append("\n【分部单点换算】收入 $%.1fB 的利润率每变动 %dbp → 税前 $%sM"
               % (seg["收入 $B"], seg["变动 bp"], int(seg["税前 $M"]))
               + f" → EPS {seg['EPS 影响 $']:+.2f}（{seg['占 EPS %']:+.1f}%）")
    return "\n".join(out)


PEP_2026_11 = dict(
    eps=8.40, shares_m=1363, tax=0.24, conv=0.68,
    fcf_b=7.90, div_b=8.07, ebitda_b=19.17, netdebt_b=40.718,
    price=141.88, multiple=16.9,
)

if __name__ == "__main__":
    print(render(build(PEP_2026_11)))
