"""
A股 DuPont ROE + DCF 内在价值财务建模模板
===================================================
专用单位体系：亿 RMB（营收/净利/资产/市值），元/股（EPS/BVPS/股价），亿股（总股本）

⚠️ 与美股模板 `dupont_analysis.py` 的关键差异：
  美股模板用 billion USD + million shares → equity = bvps * shares_m / 10000
  本模板用 亿 RMB + 亿 shares     → equity = bvps * shares_total  （亿股 × 元/股 = 亿元）
  
  如果把美股模板的公式直接套A股，DuPont会算出1273%的ROE、DCF IV会到¥1300+。
  检查方法：跑完模型后手算 PE=股价/EPS，与模型输出的PE对比——不匹配说明单位出错了。

Usage: 在 execute_code 中运行，替换 data 区域的值即可。
"""

# ============================================================
# 1. 填入数据（亿 RMB，EPS/BVPS/股价为元）
# ============================================================
company = "公司名"
ticker = "代码"
stock_price = 0.0         # 当前股价 元
market_cap = 0.0          # 总市值 亿 RMB
shares_total = 0.0        # 总股本 亿股（= 百万股 / 100）

years = [2021, 2022, 2023, 2024, 2025]

# 年度财务数据（亿 RMB）
rev     = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 营收 亿
ni      = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 归母净利 亿
eps     = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 每股收益 元
bvps    = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 每股净资产 元
ocf     = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 经营现金流 亿
capex   = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 资本支出 亿
fcf     = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 自由现金流 亿
div_ps  = {2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 0.0}  # 每股分红 元

# 资产负债表（最新年，亿 RMB）
total_assets = 0.0        # 总资产 亿
total_liab   = 0.0        # 总负债 亿
equity_book  = 0.0        # 净资产 亿（应 ≈ BVPS × shares_total）
cash         = 0.0        # 货币资金 亿
lt_debt      = 0.0        # 长期有息负债 亿
goodwill     = 0.0        # 商誉+无形资产 亿

# DCF 假设
base_fcf   = fcf[2025]    # 起步 FCF（亿）
wacc       = 0.10         # 加权资本成本
terminal_g = 0.03         # 永续增长率
growth_low  = 0.06        # 保守增速
growth_mid  = 0.09        # 基准增速
growth_high = 0.12        # 乐观增速
n_yr        = 5           # 高增长年数

# ============================================================
# 2. CAGR 分析
# ============================================================
print("=" * 60)
print(f"{company} ({ticker}) — A-Share DuPont + DCF Model")
print("=" * 60)
print(f"\n📈 1. CAGR Analysis ({years[0]}-{years[-1]})")

for name, d in [("营收", rev), ("净利", ni), ("EPS", eps), ("BVPS", bvps), ("OCF", ocf), ("FCF", fcf)]:
    cagr = (d[years[-1]] / d[years[0]]) ** (1/(len(years)-1)) - 1 if d[years[0]] else 0
    print(f"  {name}: {d[years[0]]:.1f} → {d[years[-1]]:.1f}, CAGR = {cagr*100:.1f}%")

# ============================================================
# 3. 利润率趋势
# ============================================================
print("\n📊 2. Profitability")
for y in years:
    nm = ni[y] / rev[y] * 100 if rev[y] else 0
    roe_y = eps[y] / bvps[y] * 100 if bvps[y] else 0
    print(f"  {y}: Rev={rev[y]:.0f}亿, NI={ni[y]:.1f}亿, NetM={nm:.1f}%, ROE={roe_y:.1f}%")

# ============================================================
# 4. DuPont ROE 拆解 ⚠️ KEY: 用亿元+亿股，不是亿美元+百万股
# ============================================================
print("\n🔍 3. DuPont ROE Decomposition")
print("   ROE = NetMargin × AssetTurnover × EquityMultiplier")

# 每股净资产 × 总股本 = 净资产（亿）——这是A股模板的核心公式
eq_latest = shares_total * bvps[years[-1]]  # 亿

# 每一年用不同的EM估算值（制造商1.3-2.5x范围）
em_estimates = {2021: 1.30, 2022: 1.35, 2023: 1.40, 2024: 1.55, 2025: total_assets/equity_book if total_assets and equity_book else 1.44}

for y in years:
    nm = ni[y] / rev[y] * 100 if rev[y] else 0
    eq_y = shares_total * bvps[y]    # ← A股公式：亿股 × 元/股 = 亿元
    em = em_estimates.get(y, 1.50)
    ta_y = eq_y * em
    at = rev[y] / ta_y if ta_y else 0
    roe_dupont = (nm/100) * at * em * 100
    actual_roe = eps[y] / bvps[y] * 100 if bvps[y] else 0
    print(f"  {y}: ROE={actual_roe:.1f}% | NM={nm:.1f}% | AT={at:.2f} | EM={em:.2f}x | Dupont={roe_dupont:.1f}%")

# ============================================================
# 5. 现金流质量
# ============================================================
print("\n💰 4. Cash Flow Quality")
for y in years:
    ocf_ps = ocf[y] / shares_total if shares_total else 0    # ← A股公式：亿 / 亿股 = 元/股
    fcf_ps = fcf[y] / shares_total if shares_total else 0
    capex_pct = capex[y] / rev[y] * 100 if rev[y] else 0
    print(f"  {y}: OCF/EPS={ocf_ps/eps[y]:.2f}x | FCF/EPS={fcf_ps/eps[y]:.2f}x | CapEx/Rev={capex_pct:.1f}%")

# ============================================================
# 6. 估值指标
# ============================================================
print("\n💎 5. Current Valuation")
pe   = stock_price / eps[years[-1]] if eps[years[-1]] else 0
pb   = market_cap / equity_book if equity_book else 0
ps   = market_cap / rev[years[-1]] if rev[years[-1]] else 0
roe  = eps[years[-1]] / bvps[years[-1]] * 100 if bvps[years[-1]] else 0
pe_roe_ratio = pe / roe * 100 if roe else 0
fcf_yield = fcf[years[-1]] / market_cap * 100 if market_cap else 0
net_debt = lt_debt - cash
ev = market_cap + net_debt

print(f"  股价:           ¥{stock_price:.1f}")
print(f"  市值:           ¥{market_cap:.0f}亿")
print(f"  总股本:         {shares_total:.1f}亿股")
print(f"  P/E (TTM):      {pe:.1f}x")
print(f"  P/B:            {pb:.2f}x")
print(f"  P/S:            {ps:.2f}x")
print(f"  ROE:            {roe:.1f}%")
print(f"  PE/ROE:         {pe_roe_ratio:.2f}")
print(f"  FCF Yield:      {fcf_yield:.1f}%")
print(f"  Div Yield:      {div_ps[years[-1]]/stock_price*100:.1f}%" if stock_price else "")
print(f"  Net Debt:       ¥{net_debt:.0f}亿")
print(f"  EV:             ¥{ev:.0f}亿")
print(f"  EV/Rev:         {ev/rev[years[-1]]:.2f}x" if rev[years[-1]] else "")

# ============================================================
# 7. DCF 内在价值 ⚠️ A股公式：IV = equity_value / shares_total (亿/亿股 = 元/股)
# ============================================================
print("\n🔮 6. DCF Intrinsic Value")
for label, g in [("Conservative", growth_low), ("Base", growth_mid), ("Optimistic", growth_high)]:
    fcf_series = [base_fcf * (1+g)**i for i in range(1, n_yr+1)]
    pv_fcf = sum(fcf_series[i] / (1+wacc)**(i+1) for i in range(n_yr))
    tv = fcf_series[-1] * (1+terminal_g) / (wacc - terminal_g)
    pv_tv = tv / (1+wacc)**n_yr
    ev_dcf = pv_fcf + pv_tv
    eq_dcf = ev_dcf + cash - lt_debt
    iv = eq_dcf / shares_total if shares_total else 0  # ← A股公式：亿 / 亿股 = 元/股
    upside = (iv/stock_price - 1) * 100 if stock_price else 0
    print(f"  {label:15s} ({g*100:.0f}%): IV=¥{iv:.1f} | EV=¥{ev_dcf:.0f}亿 | {'↑' if upside>0 else '↓'} {abs(upside):.0f}%")

# ============================================================
# 8. PEG
# ============================================================
print("\n📐 7. PEG")
eps_cagr = (eps[years[-1]] / eps[years[0]]) ** (1/(len(years)-1)) - 1 if eps[years[0]] else 0
peg = pe / (eps_cagr * 100) if eps_cagr else 0
print(f"  EPS CAGR: {eps_cagr*100:.1f}%")
print(f"  PEG:       {peg:.2f}")

# ============================================================
# 9. ROE 可持续性检查
# ============================================================
print("\n⚠️ 8. ROE Sustainability Check")
print(f"  Current ROE: {roe:.1f}%")
if roe > 30:
    print(f"  ⚠ ROE 异常高位，需做均值回归分析")
    for norm_roe in [22, 18, 15]:
        norm_eps = norm_roe/100 * bvps[years[-1]]
        norm_pe = stock_price / norm_eps
        print(f"    ROE→{norm_roe}%: EPS=¥{norm_eps:.2f}, P/E={norm_pe:.1f}x")
elif roe > 20:
    print(f"  ROE 偏高但可能可持续。如果在扩张期，ROE被CapEx稀释，正常化后可能更高。")
else:
    print(f"  ROE 在正常范围，不需要均值回归预警。")

print("\n" + "=" * 60)
print("MODEL COMPLETE — Verify: PE=股价/EPS 应与上方一致")
print("=" * 60)
