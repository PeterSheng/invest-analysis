"""
Brown & Brown (BRO) — DuPont ROE + DCF Intrinsic Value Model
================================================================
Template for four-master investment analysis financial modeling.

Usage: run via execute_code(). Edit the `data` dict with company-specific
values from web_search data collection, then run to get the full model output.
"""

import json, math

# ============================================================
# COMPANY DATA — Fill in from data collection phase
# ============================================================
data = {
    "company": "COMPANY_NAME",
    "ticker": "TICKER",
    "report_date": "YYYY-MM-DD",

    # Market Data (current)
    "market": {
        "stock_price": 0.0,
        "market_cap_b": 0.0,
        "shares_outstanding_m": 0,
        "52w_high": 0.0,
        "52w_low": 0.0,
        "dividend_per_share": 0.0,
        "dividend_yield_pct": 0.0,
        "payout_ratio_pct": 0.0,
    },

    # 5-year Annual Financials
    "annual": {
        "revenue_b":     {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "net_income_b":  {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "eps":           {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "operating_cf_b":{0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "capex_b":       {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "fcf_b":         {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "bvps":          {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "dividends":     {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "years":         [2020, 2021, 2022, 2023, 2024],
    },

    # Post-major-event estimates (M&A, restructuring, etc.)
    "event": {
        "description": "",
        "added_revenue_b": 0.0,
        "q_recent_revenue_b": 0.0,
        "q_recent_net_income_b": 0.0,
        "q_recent_gaap_eps": 0.0,
        "q_recent_adj_eps": 0.0,
    },

    # Balance Sheet
    "balance_sheet": {
        "total_assets_b": 0.0,
        "total_liabilities_b": 0.0,
        "equity_b": 0.0,
        "cash_b": 0.0,
        "long_term_debt_b": 0.0,
        "goodwill_intangibles_b": 0.0,
        "ebit_b": 0.0,
        "interest_coverage": 0.0,
    },

    # DCF assumptions
    "dcf": {
        "base_fcf_b": 0.0,      # starting FCF (annualized)
        "growth_low": 0.08,
        "growth_mid": 0.10,
        "growth_high": 0.12,
        "wacc": 0.10,
        "terminal_g": 0.03,
        "high_growth_years": 5,
    },
}

years = data["annual"]["years"]
n_years = len(years)

# ============================================================
# 1. CAGR Analysis
# ============================================================
print("=" * 60)
print(f"{data['company']} ({data['ticker']}) — FINANCIAL MODEL")
print("=" * 60)
print(f"\n📈 1. CAGR Analysis ({years[0]}-{years[-1]})")

metrics_cagr = {}
for metric_name, values in data["annual"].items():
    if metric_name in ("dividends", "years"):
        continue
    start = values[0]
    end = values[n_years - 1]
    cagr = (end / start) ** (1 / (n_years - 1)) - 1
    metrics_cagr[metric_name] = cagr
    print(f"  {metric_name}: {start:.2f} → {end:.2f}, CAGR = {cagr*100:.1f}%")

# ============================================================
# 2. Profitability Ratios
# ============================================================
print("\n📊 2. Profitability Ratios")
for i, year in enumerate(years):
    rev = data["annual"]["revenue_b"][i]
    ni = data["annual"]["net_income_b"][i]
    margin = ni / rev * 100 if rev else 0
    print(f"  {year}: Net Margin = {margin:.1f}%")

# ============================================================
# 3. DuPont ROE Decomposition
# ============================================================
print("\n🔍 3. DuPont ROE Decomposition")
print("   ROE = Net Margin × Asset Turnover × Equity Multiplier")

# ⚠️ PITFALL: Do NOT use a single global est_equity_mult for all years.
# If you have actual balance sheet data for the latest year but only estimated
# BVPS for historical years, the global EM will produce nonsense for years where
# equity was very different (e.g. EM=140 when equity estimate doesn't match assets).
# 
# FIX: Estimate EM per-year from annual data, or fall back to per-year estimates.
# The key insight: DuPont is for TREND DIRECTION (NM↑/↓, AT↑/↓, EM↑/↓), not
# absolute precision. See pitfall in SKILL.md: "DuPont ROE与报告ROE数字不匹配时恐慌".
#
# For years where you have actual balance sheet:
#   em = total_assets / equity
# For years where you only have BVPS:
#   Use industry-typical EM (1.3-2.5x for manufacturers; ~1.4x for asset-light cash-rich like 恒立)
#   Or estimate from trend: if debt ratio is stable, EM is stable; if paying down debt, EM declines.

for i, year in enumerate(years):
    rev = data["annual"]["revenue_b"][i]
    ni = data["annual"]["net_income_b"][i]
    bvps = data["annual"]["bvps"][i]
    eps = data["annual"]["eps"][i]
    roe_actual = eps / bvps * 100 if bvps else 0

    net_margin = ni / rev * 100 if rev else 0
    equity = bvps * data["market"]["shares_outstanding_m"] / 1000 if data["market"]["shares_outstanding_m"] else 0  # 美股: bvps($)×shares(M)=$M → /1000=$B。⚠️勿用 /10000（A股单位习惯误植，会让equity少10倍、AT虚高10倍）

    # Per-year EM: use actual B/S if available for that year, else estimate
    if i == (n_years - 1) and data["balance_sheet"]["equity_b"]:
        # Latest year: use actual balance sheet
        total_assets_i = data["balance_sheet"]["total_assets_b"]
        em = total_assets_i / data["balance_sheet"]["equity_b"]
    else:
        # Historical years: estimate EM from debt ratio trend
        # Cash-rich manufacturers: 1.3-2.0x; leveraged ones: 2.0-3.5x
        # 恒立 is cash-rich (~30% debt ratio) → EM ≈ 1.4x
        em = 1.8 if i < 2 else 1.6 if i < 4 else 1.4
        total_assets_i = equity * em
    
    asset_turnover = rev / total_assets_i if total_assets_i else 0
    roe_dupont = net_margin / 100 * asset_turnover * em * 100
    print(f"  {year}: ROE={roe_actual:.1f}% | NM={net_margin:.1f}% | AT={asset_turnover:.2f} | EM={em:.2f}x | DupontCheck={roe_dupont:.1f}%")

# ============================================================
# 4. Cash Flow Quality
# ============================================================
print("\n💰 4. Cash Flow Quality (OCF/EPS & FCF/EPS)")
shares_m = data["market"]["shares_outstanding_m"] or 100

for i, year in enumerate(years):
    ocf_b = data["annual"]["operating_cf_b"][i]
    fcf_b = data["annual"]["fcf_b"][i]
    eps = data["annual"]["eps"][i]
    capex_b = data["annual"]["capex_b"][i]
    rev_b = data["annual"]["revenue_b"][i]

    ocf_per_share = ocf_b * 1000 / shares_m if shares_m else 0
    fcf_per_share = fcf_b * 1000 / shares_m if shares_m else 0
    ocf_eps_ratio = ocf_per_share / eps if eps else 0
    fcf_eps_ratio = fcf_per_share / eps if eps else 0
    capex_pct = capex_b / rev_b * 100 if rev_b else 0

    print(f"  {year}: OCF/EPS={ocf_eps_ratio:.2f}x | FCF/EPS={fcf_eps_ratio:.2f}x | CapEx/Rev={capex_pct:.1f}%")

# ============================================================
# 5. Valuation Metrics
# ============================================================
print("\n💎 5. Current Valuation")
price = data["market"]["stock_price"]
mkt_cap = data["market"]["market_cap_b"]
shares = data["market"]["shares_outstanding_m"]

# Annualize from latest quarter
q_rev = data["event"]["q_recent_revenue_b"]
q_ni = data["event"]["q_recent_net_income_b"]
q_eps_gaap = data["event"]["q_recent_gaap_eps"]
q_eps_adj = data["event"]["q_recent_adj_eps"]

if q_rev:
    ann_rev = q_rev * 4
    ann_ni = q_ni * 4
    ann_eps_gaap = q_eps_gaap * 4
    ann_eps_adj = q_eps_adj * 4
else:
    # Fallback to last annual
    ann_rev = data["annual"]["revenue_b"][n_years - 1]
    ann_ni = data["annual"]["net_income_b"][n_years - 1]
    ann_eps_gaap = data["annual"]["eps"][n_years - 1]
    ann_eps_adj = ann_eps_gaap

pe_gaap = price / ann_eps_gaap if ann_eps_gaap else 0
pe_adj = price / ann_eps_adj if ann_eps_adj else 0
ps = mkt_cap / ann_rev if ann_rev else 0
pb = price / (data["balance_sheet"]["equity_b"] * 1000 / shares) if data["balance_sheet"]["equity_b"] and shares else 0

ann_fcf = data["dcf"]["base_fcf_b"]
fcf_yield = ann_fcf / mkt_cap * 100 if mkt_cap else 0

net_debt = data["balance_sheet"]["long_term_debt_b"] - data["balance_sheet"]["cash_b"]
ev = mkt_cap + net_debt

print(f"  Stock Price:       ${price:.2f}")
print(f"  Market Cap:        ${mkt_cap:.2f}B")
print(f"  Est Ann Rev:       ${ann_rev:.1f}B")
print(f"  Est Ann NI:        ${ann_ni:.2f}B")
print(f"  P/E (GAAP):        {pe_gaap:.1f}x")
print(f"  P/E (Adj):         {pe_adj:.1f}x")
print(f"  P/S:               {ps:.2f}x")
print(f"  P/B:               {pb:.2f}x")
print(f"  FCF Yield:         {fcf_yield:.1f}%")
print(f"  EV/Rev:            {ev/ann_rev:.1f}x" if ann_rev else "")
print(f"  EV/EBIT:           {ev/data['balance_sheet']['ebit_b']:.1f}x" if data['balance_sheet']['ebit_b'] else "")

# ============================================================
# 6. DCF Intrinsic Value (3 scenarios)
# ============================================================
print("\n🔮 6. DCF Intrinsic Value Estimate")

base_fcf = data["dcf"]["base_fcf_b"]
wacc = data["dcf"]["wacc"]
terminal_g = data["dcf"]["terminal_g"]
n_yr = data["dcf"]["high_growth_years"]

scenarios = {
    "Conservative": data["dcf"]["growth_low"],
    "Base": data["dcf"]["growth_mid"],
    "Optimistic": data["dcf"]["growth_high"],
}

results = {}
for name, growth in scenarios.items():
    fcf_series = [base_fcf * (1 + growth) ** i for i in range(1, n_yr + 1)]
    pv_fcf = sum([fcf_series[i] / (1 + wacc) ** (i + 1) for i in range(n_yr)])
    terminal_value = fcf_series[-1] * (1 + terminal_g) / (wacc - terminal_g)
    pv_terminal = terminal_value / (1 + wacc) ** n_yr
    ev_scenario = pv_fcf + pv_terminal
    eq_scenario = ev_scenario + data["balance_sheet"]["cash_b"] - data["balance_sheet"]["long_term_debt_b"]
    iv = eq_scenario * 1000 / shares if shares else 0
    upside = (iv / price - 1) * 100 if price else 0
    results[name] = {"iv": round(iv, 2), "upside_pct": round(upside, 1)}
    print(f"  {name} ({growth*100:.0f}% growth): IV=${iv:.2f} | {'↑' if upside>0 else '↓'} {abs(upside):.0f}%")

# ============================================================
# 7. PEG Ratio
# ============================================================
print("\n📐 7. Growth & PEG")

eps_start = data["annual"]["eps"][0]
eps_end = data["annual"]["eps"][n_years - 1]
eps_growth_hist = (eps_end / eps_start) ** (1 / (n_years - 1)) - 1 if eps_start else 0
peg_hist = pe_gaap / (eps_growth_hist * 100) if eps_growth_hist else 0

print(f"  EPS CAGR ({years[0]}-{years[-1]}):   {eps_growth_hist*100:.1f}%")
print(f"  PEG (Historical):                    {peg_hist:.2f}")

# Forward PEG
if ann_eps_adj and eps_end:
    fwd_growth = (ann_eps_adj / eps_end) ** (1 / 2) - 1  # assume 2yr forward
    peg_fwd = pe_adj / (fwd_growth * 100) if fwd_growth else 0
    print(f"  EPS CAGR (Hist→Fwd Est):             {fwd_growth*100:.1f}%")
    print(f"  PEG (Forward):                       {peg_fwd:.2f}")

# ============================================================
# 8. Summary (for embedding in reports)
# ============================================================
print("\n" + "=" * 60)
print("MODEL SUMMARY")
print("=" * 60)
summary = {
    "cagr_revenue": round(metrics_cagr.get("revenue_b", 0) * 100, 1),
    "cagr_net_income": round(metrics_cagr.get("net_income_b", 0) * 100, 1),
    "cagr_eps": round(metrics_cagr.get("eps", 0) * 100, 1),
    "net_margin_latest": round(data["annual"]["net_income_b"][n_years - 1] / data["annual"]["revenue_b"][n_years - 1] * 100, 1),
    "roe_latest": round(data["annual"]["eps"][n_years - 1] / data["annual"]["bvps"][n_years - 1] * 100, 1),
    "fcf_ni_ratio_latest": round(data["annual"]["fcf_b"][n_years - 1] / data["annual"]["net_income_b"][n_years - 1] * 100, 1),
    "pe_gaap": round(pe_gaap, 1),
    "ps": round(ps, 2),
    "pb": round(pb, 2),
    "fcf_yield_pct": round(fcf_yield, 1),
    "iv_conservative": results["Conservative"]["iv"] if "Conservative" in results else 0,
    "iv_base": results["Base"]["iv"] if "Base" in results else 0,
    "iv_optimistic": results["Optimistic"]["iv"] if "Optimistic" in results else 0,
    "current_price": price,
    "upside_base_pct": results["Base"]["upside_pct"] if "Base" in results else 0,
}
for k, v in summary.items():
    print(f"  {k}: {v}")
