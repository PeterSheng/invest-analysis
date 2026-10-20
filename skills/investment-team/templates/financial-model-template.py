"""
============================================================
  DuPont ROE + DCF 内在价值财务建模模板
  适用于: 加盟/零售/消费类公司（轻资产模式）
  依赖: 仅需 Python 标准库
  使用: 复制到 execute_code，填入 data 字典后运行
============================================================
"""

# ============================================================
# 财务数据 (填入实际数据)
# 单位: 亿元人民币(除每股数据外)，或美元(标注)
# ============================================================
data = {
    "company": "公司名 (TICKER)",
    "shares": 3.796,       # 总股本 (亿股)
    "current_price": 253.0, # 当前股价
    "currency_to_rmb": 1.0, # 汇率 (港股≈0.92, 美股≈7.2)
    "years": [2022, 2023, 2024, 2025],

    # 利润表
    "revenue":         [136.0, 203.0, 248.3, 335.0],
    "gross_profit":    [40.0,  60.9,  78.0,  102.0],
    "operating_profit":[24.0,  38.0,  52.0,  70.0],
    "net_profit":      [20.0,  32.0,  44.5,  59.27],

    # 资产负债表 (如无准确数据，用合理估计)
    "total_assets":    [90.0,  130.0, 180.0, 240.0],
    "total_equity":    [55.0,  80.0,  110.0, 160.0],
    "cash":            [30.0,  50.0,  111.1, 140.0],
    "interest_bearing_debt": [5.0, 3.0, 2.0, 2.0],

    # 现金流 (OCF 和 CapEx，FCF = OCF - CapEx)
    "ocf":             [22.0,  35.0,  48.0,  65.0],
    "capex":           [8.0,   10.0,  12.0,  15.0],

    # 运营数据 (可选，用于上下文)
    "stores":          [29000, 36000, 46479, 59000],
}

# ============================================================
# 计算派生指标 (无需修改)
# ============================================================

price = data["current_price"] * data["currency_to_rmb"]
market_cap = price * data["shares"]

n = len(data["years"])
rev = data["revenue"]
np_ = data["net_profit"]
eq = data["total_equity"]
ast = data["total_assets"]
ocf = data["ocf"]
capex = data["capex"]
fcf = [ocf[i] - capex[i] for i in range(n)]

# 每股指标
eps = [np_[i] / data["shares"] for i in range(n)]
bvps = [eq[i] / data["shares"] for i in range(n)]
fcf_ps = [fcf[i] / data["shares"] for i in range(n)]

# 利润率
gm = [data["gross_profit"][i]/rev[i]*100 for i in range(n)]
nm = [np_[i]/rev[i]*100 for i in range(n)]
roe = [np_[i]/eq[i]*100 for i in range(n)]

# CAGR (3年，从 index[1] 到 index[-1])
rev_cagr = ((rev[-1]/rev[1])**(1/(n-2))-1)*100
np_cagr = ((np_[-1]/np_[1])**(1/(n-2))-1)*100
eps_cagr = ((eps[-1]/eps[1])**(1/(n-2))-1)*100

# DuPont ROE 拆解 (最新年)
nm_latest = nm[-1]
at_latest = rev[-1] / ast[-1]  # 资产周转率
em_latest = ast[-1] / eq[-1]   # 权益乘数
roe_dup = nm_latest/100 * at_latest * em_latest * 100

# 估值
pe = market_cap / np_[-1]
pb = market_cap / eq[-1]
peg = pe / eps_cagr if eps_cagr > 0 else float('inf')
ocf_ratio = ocf[-1] / np_[-1]
fcf_yield = fcf_ps[-1] / price * 100

# ============================================================
# ROE 均值回归分析 (当 ROE > 25% 时必须输出)
# ============================================================
# 原理：高 ROE 不可持续。当 ROE 向行业正常水平回归时，
# 市场通常会同步压缩 PB 倍数。正确公式由两个独立效应组成：
#
#   效应1（PB 不变）：PE_new = PB / (ROE_norm/100)
#   效应2（PB 回归）：PB_norm = ROE_norm / (ROE[-1]/100) * PB
#                     PE_norm = PB_norm / (ROE_norm/100)
#                     Price_norm = PB_norm * bvps[-1]
#
# 实际场景通常是效应1+2的组合：PB 从异常高位回归到正常水平。
# 如果不做这个分析，PE/ROE 排名会把高 ROE 公司误判为"极度低估"。

if roe[-1] > 25.0:
    norm_roe_values = [25.0, 22.0, 20.0, 18.0]
    for norm_roe in norm_roe_values:
        if norm_roe >= roe[-1]:
            continue
        # 效应1: PB不变, PE被动升高
        pe_if_pb_flat = pb / (norm_roe / 100)
        # 效应2: PB随ROE比例收缩
        pb_normalized = (norm_roe / 100) / (roe[-1] / 100) * pb
        pe_normalized = pb_normalized / (norm_roe / 100)
        price_normalized = pb_normalized * bvps[-1]
        mos_norm = (price_normalized / data["current_price"] - 1) * 100
        print(f"  ROE→{norm_roe:.0f}%: PB={pb_normalized:.1f}x PE={pe_normalized:.0f}x 合理价={price_normalized:.0f}元 ({mos_norm:+.0f}%)  PE/ROE={pe_normalized/norm_roe:.2f}")
# ⚠️ DCF 增长率假设必须与公司实际营收 CAGR 校准：
#    模板默认 g1=12% g2=8% 只适用高速成长公司（营收 CAGR>10%）。
#    成熟/低增速消费公司（营收 CAGR<5%，如百胜中国 3.3%）必须手动改为
#    g1=8-10%、g2=6-7%、tg=2.5-3%，否则 IV 虚高、安全边际误判（百胜中国实战教训）。
# ============================================================
# DCF 内在价值 (简化两阶段模型)
# ============================================================
base_fcf = fcf[-1]
wacc = 10.0        # 折现率
g1 = 12.0          # 阶段1 (1-5年) 增长率
g2 = 8.0           # 阶段2 (6-10年) 增长率
tg = 3.0           # 永续增长率

pv_sum = 0.0
cf = base_fcf
for yr in range(1, 11):
    g = g1/100 if yr <= 5 else g2/100
    cf *= (1+g)
    pv_sum += cf / ((1+wacc/100)**yr)

tv = cf * (1+tg/100) / (wacc/100 - tg/100)
pv_tv = tv / ((1+wacc/100)**10)
net_cash = data["cash"][-1] - data["interest_bearing_debt"][-1]
eq_val = pv_sum + pv_tv + net_cash
iv_per_share = eq_val / data["shares"] / data["currency_to_rmb"]
mos = (iv_per_share / data["current_price"] - 1) * 100

# ============================================================
# 输出
# ============================================================
print("=" * 60)
print(f"  {data['company']} 财务建模报告")
print("=" * 60)

print(f"\n[市场数据] 股价: {data['current_price']:.0f}  市值: {market_cap:.0f}亿")

print(f"\n[历史财务]")
print(f"  {'年份':<6} {'营收':>8} {'净利':>8} {'GM%':>6} {'NM%':>6} {'ROE%':>6} {'EPS':>7}")
print(f"  {'-'*55}")
for i in range(n):
    print(f"  {data['years'][i]:<6} {rev[i]:>8.0f} {np_[i]:>8.1f} {gm[i]:>6.1f} {nm[i]:>6.1f} {roe[i]:>6.1f} {eps[i]:>7.2f}")

print(f"\n[增长率] 营收CAGR: {rev_cagr:.1f}%  净利CAGR: {np_cagr:.1f}%  EPS CAGR: {eps_cagr:.1f}%")

print(f"\n[DuPont ROE] {roe[-1]:.1f}% = 净利率{nm_latest:.1f}% x 周转率{at_latest:.2f}x x 杠杆{em_latest:.2f}x")

print(f"\n[估值] PE: {pe:.1f}x  PB: {pb:.1f}x  PEG: {peg:.2f}x  FCF Yield: {fcf_yield:.1f}%  OCF/NP: {ocf_ratio:.2f}x")

print(f"\n[DCF] WACC={wacc:.0f}% g1={g1:.0f}% g2={g2:.0f}% tg={tg:.0f}%")
print(f"  内在价值/股: {iv_per_share:.0f}  安全边际: {mos:+.1f}%")

# 敏感性分析
print(f"\n[DCF 敏感性: WACC vs 永续增长率]")
wg_range = [8, 9, 10, 11, 12]
tg_range = [2.0, 2.5, 3.0, 3.5, 4.0]
sep = "  "
print(f"  WACC\\TG{sep}", end="")
for t in tg_range:
    print(f"{t:.1f}%{sep}", end=" ")
print()
for w in wg_range:
    print(f"  {w:.1f}%{sep*2}", end="")
    for t in tg_range:
        pv2 = 0.0
        cf2 = base_fcf
        for yr in range(1, 11):
            g = g1/100 if yr <= 5 else g2/100
            cf2 *= (1+g)
            pv2 += cf2 / ((1+w/100)**yr)
        tv2 = cf2 * (1+t/100) / (w/100 - t/100)
        pvt2 = tv2 / ((1+w/100)**10)
        eq2 = pv2 + pvt2 + net_cash
        iv2 = eq2 / data["shares"] / data["currency_to_rmb"]
        m2 = (iv2/data["current_price"]-1)*100
        print(f"{m2:+.0f}%{sep}", end=" ")
    print()

print(f"\n[DONE]")
