#!/usr/bin/env python3
"""
DCF 三情景估值 + 市场隐含增速分析 — 通用可复用模板

Usage: python3 dcf_three_scenario.py

Copy this file and modify the BASE PARAMETERS section for each stock.
Keep the rest of the computation section unchanged.

Key inputs:
  - shares: 总股本(亿)
  - price: 当前股价
  - ttm_np: TTM归母净利(亿) = Q1最新 + (上年FY - 上年Q1)
  - ttm_rev: TTM营收(亿) = Q1最新 + (上年FY - 上年Q1)
  - fcf_conv: FCF/净利比例 (医疗器械 0.85, CDMO 0.80, 消费品 0.90)

For each scenario, define:
  - desc: scenario description
  - rev_g[N]: revenue growth rate for year N (N=1..10)
  - npm[N]: net profit margin for year N
  - tpe: terminal PE multiple (for PE-based cross-check)

Output includes:
  1. Three-scenario DCF with PE terminal value cross-check
  2. Sensitivity matrix: WACC x terminal g => target price
  3. Market-implied growth: what perpetual growth does current PE embed?
  4. Current-price implied g1 (bisection) + zero-growth anchor (FCF/CoE) + EPS-path
     (fwd EPS x exit multiple discounted back) — see references/us-stock-data-sources.md 2.9

Post-mega-acquisition rule (SNPS/Ansys 2026-09): if the deal year depressed FCF
(integration costs + interest), do NOT start the DCF from the distorted TTM/FY.
Start from normalized FY N+1 FCF (guidance-extrapolated revenue x normal FCF margin).
EV-method consistency: uFCF = levered FCF + after-tax interest; equity value = EV - net debt.

Pitfall: f-string expressions CANNOT contain backslashes. Use variables instead:
    # WRONG: print(f"{'WACC\\tg':>8}")
    # RIGHT: sep = "WACC\\tg"; print(f"{sep:>8}")
"""

# ============================================================
# === BASE PARAMETERS — MODIFY FOR DIFFERENT STOCKS ===========
# ============================================================

shares = 1.8785          # 亿股 (total shares outstanding)
price = 79.80            # 当前股价 (current stock price)
ttm_np = 5.55            # TTM归母净利(亿) (trailing 12-month net profit)
ttm_rev = 33.39          # TTM营收(亿) (trailing 12-month revenue)
fcf_conv = 0.85          # FCF转换率 (free cash flow as % of net profit)

WACC = 0.10              # 折现率 (discount rate)
terminal_g = 0.03        # 永续增长率 (terminal growth rate)
years = 10               # 预测期 (forecast horizon)

# === SCENARIO DEFINITIONS ====================================
# rev_g: revenue growth rates for years 1-10
# npm:   net profit margin trajectory for years 1-10
# tpe:   terminal PE multiple for PE-based valuation check

scenarios = {
    "悲观": {
        "desc": "集采扩面+竞争加剧+海外受阻",
        "rev_g": [0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03],
        "npm":   [0.165, 0.160, 0.155, 0.150, 0.145, 0.140, 0.138, 0.135, 0.133, 0.130],
        "tpe": 18,
    },
    "基准": {
        "desc": "稳步国产替代+海外温和拓展",
        "rev_g": [0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.10, 0.09, 0.08, 0.07],
        "npm":   [0.170, 0.172, 0.175, 0.178, 0.180, 0.180, 0.182, 0.182, 0.183, 0.183],
        "tpe": 22,
    },
    "乐观": {
        "desc": "海外放量+新产品突破+集采影响有限",
        "rev_g": [0.18, 0.17, 0.16, 0.15, 0.15, 0.14, 0.13, 0.12, 0.10, 0.10],
        "npm":   [0.175, 0.180, 0.188, 0.195, 0.200, 0.205, 0.208, 0.210, 0.212, 0.215],
        "tpe": 28,
    },
}

# ============================================================
# === COMPUTATION =============================================
# ============================================================

mcap = price * shares
current_npm = ttm_np / ttm_rev
base_fcf = ttm_np * fcf_conv

print("=" * 70)
print(f"  DCF 估值模型 | 当前股价: {price:.2f}元 | 市值: {mcap:.1f}亿")
print(f"  TTM营收: {ttm_rev:.2f}亿 | TTM净利: {ttm_np:.2f}亿 | 净利率: {current_npm*100:.1f}%")
print(f"  基准FCF(起始): {base_fcf:.2f}亿 (净利x{fcf_conv})")
print(f"  WACC: {WACC*100:.0f}% | 永续g: {terminal_g*100:.0f}% | 预测期: {years}年")
print("=" * 70)

emoji_map = {"悲观": "🐢", "基准": "🚶", "乐观": "🚀"}
scenario_iv_ps = {}   # 反向DCF落点判读用：各情景每股IV

for name, params in scenarios.items():
    emoji = emoji_map[name]
    print(f"\n--- {emoji} {name}: {params['desc']} ---")

    rev = ttm_rev
    total_pv = 0

    for yr in range(years):
        g = params["rev_g"][yr]
        npm = params["npm"][yr]
        rev *= (1 + g)
        np = rev * npm
        fcf = np * fcf_conv
        pv = fcf / ((1 + WACC) ** (yr + 1))
        total_pv += pv

    # DCF terminal value
    final_np = rev * params["npm"][-1]
    final_fcf = final_np * fcf_conv
    term_val = final_fcf * (1 + terminal_g) / (WACC - terminal_g)
    term_pv = term_val / ((1 + WACC) ** years)

    total_val = total_pv + term_pv
    per_share = total_val / shares
    upside = (per_share / price - 1) * 100
    scenario_iv_ps[name] = per_share   # 供反向DCF落点判读使用

    # PE terminal value (cross-check)
    pe_term_val = final_np * params["tpe"]
    pe_term_pv = pe_term_val / ((1 + WACC) ** years)
    pe_total = total_pv + pe_term_pv
    pe_ps = pe_total / shares
    pe_upside = (pe_ps / price - 1) * 100

    print(f"  DCF终值: 预测期PV={total_pv:.1f}亿 + 终值PV={term_pv:.1f}亿")
    print(f"          总估值={total_val:.1f}亿 | 每股={per_share:.1f}元 | vs现价: {upside:+.0f}%")
    print(f"  PE终值({params['tpe']}x): 总估值={pe_total:.1f}亿 | 每股={pe_ps:.1f}元 | vs现价: {pe_upside:+.0f}%")

# === Sensitivity Matrix (base scenario) ======================
print(f"\n{'='*70}")
print(f"  敏感性矩阵: 基准情景 WACC x 永续g => 目标价(元)")
print(f"{'='*70}")
sc = scenarios["基准"]
wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
tg_range = [0.02, 0.03, 0.04]

header = "WACC\\tg"
print(f"  {header:<10}", end="")
for tg in tg_range:
    print(f"  {tg*100:>4.0f}%", end="")
print()

for w in wacc_range:
    print(f"  {w*100:<8.0f}%", end="")
    for tg in tg_range:
        rev = ttm_rev
        total_pv = 0
        for yr in range(years):
            rev = rev * (1 + sc["rev_g"][yr])
            np = rev * sc["npm"][yr]
            fcf = np * fcf_conv
            total_pv += fcf / ((1 + w) ** (yr + 1))

        final_np = rev * sc["npm"][-1]
        final_fcf = final_np * fcf_conv
        tv = final_fcf * (1 + tg) / (w - tg)
        tv_pv = tv / ((1 + w) ** years)
        target = (total_pv + tv_pv) / shares
        print(f"  {target:>5.0f}", end="")
    print()

# === Market-Implied Growth ===================================
print(f"\n{'='*70}")
print(f"  市场隐含增速分析 (PE={mcap/ttm_np:.1f}x)")
print(f"{'='*70}")
for implied_g in [0.03, 0.05, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]:
    rev = ttm_rev
    total_pv = 0
    for yr in range(10):
        rev = rev * (1 + implied_g)
        np = rev * current_npm
        fcf = np * fcf_conv
        total_pv += fcf / (1.10 ** (yr + 1))
    final_np = rev * current_npm
    final_fcf = final_np * fcf_conv
    tv = final_fcf * 1.03 / 0.07
    tv_pv = tv / (1.10 ** 10)
    imp_mcap = total_pv + tv_pv
    imp_price = imp_mcap / shares
    diff = (imp_price / price - 1) * 100
    marker = "  *** 接近现价 ***" if -8 < diff < 8 else ""
    print(f"  永续增速={implied_g*100:>5.0f}%: 目标价={imp_price:>6.1f}元 ({diff:>+5.0f}%){marker}")

# ============================================================
# === REVERSE DCF（反向DCF）===================================
# ============================================================
# 核心问题："当前股价隐含了什么增长预期？"
# 方法论与口径纪律：references/reverse-dcf-analysis.md（巴菲特报告必含模块）
#
# 五维反推：
#   A. implied_g1       现价隐含的前10年FCF增速（二分法，含边界处理）
#   B. implied_tg       锁定显性期，反推永续增长率
#   C. implied_irr      买入基准情景现金流，现价隐含的10年年化回报（IRR）
#   D. implied_sustainable_fcf  EV法：现价隐含的永续可持续FCF（携程54-65%语言）
#   E. zero_growth_anchor 长期不增长情景锚 + 溢价倍数（博通3.3-4.0x语言）
#
# 口径纪律（写进报告前自检，详见 references/reverse-dcf-analysis.md）：
#   1. fcf0 必须用正常化口径（收缩释放/一次性收益剔除后），不用污染的TTM
#   2. 股本分母与现价同一时点口径（重析轮先审计首轮分母——LAMR教训）
#   3. 跑完自检：IV与现价比值落在0.3-3.0之外必是单位错
#   4. 期权价值公司（DCF全负）不适用本模块 → SOTP（references/option-value-company-modeling.md）
#   5. 口径切换：REIT用AFFO/股、银行用NI CAGR、亏损平台用分部PE/隐含CLB PE
#   6. 命中边界 = 报告边界条件（"隐含增速低于最小测试值"），禁止引用边界数值本身
#   7. 零增长锚必须附WACC敏感性（低WACC会让锚膨胀）
# ============================================================

def _dcf_value(g1, wacc, tg, fcf0, horizon=10):
    """显性期固定增速g1 + 永续tg的戈登终值。返回股权总价值（与主脚本同单位：亿）。"""
    total_pv = 0.0
    fcf = fcf0
    for yr in range(horizon):
        fcf *= (1 + g1)
        total_pv += fcf / ((1 + wacc) ** (yr + 1))
    tg_cap = min(tg, wacc - 0.005)          # 戈登公式要求 tg < WACC
    tv = fcf * (1 + tg_cap) / (wacc - tg_cap)
    return total_pv + tv / ((1 + wacc) ** horizon)


def implied_g1(price, shares, fcf0, wacc, tg=0.03, g1_lo=-0.10, g1_hi=0.40, tol=0.01):
    """二分法反推现价隐含的前10年FCF增速。
    命中边界时 hit_boundary=True —— 报告必须写"低于/高于测试范围"，禁止引用边界数值。"""
    def f(g):
        return _dcf_value(g, wacc, tg, fcf0) / shares - price
    if f(g1_lo) > 0:
        return {"hit_boundary": True, "side": "below", "range": (g1_lo, g1_hi), "g1": None}
    if f(g1_hi) < 0:
        return {"hit_boundary": True, "side": "above", "range": (g1_hi, None), "g1": None}
    lo, hi = g1_lo, g1_hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return {"hit_boundary": False, "side": None, "range": (g1_lo, g1_hi), "g1": (lo + hi) / 2}


def implied_tg(price, shares, fcf0, g1, wacc, tg_lo=0.0, tol=0.001):
    """锁定显性期增速g1，反推永续增长率。搜索上限 = WACC - 0.5%（戈登约束）。
    命中上限边界 = 现价隐含永续增速>=WACC-0.5%，属荒谬读法，须改报隐含g1或终值倍数。"""
    tg_hi = wacc - 0.005
    def f(tg):
        return _dcf_value(g1, wacc, tg, fcf0) / shares - price
    if f(tg_hi) < 0:
        return {"hit_boundary": True, "side": "above", "range": (tg_lo, tg_hi), "tg": None}
    if f(tg_lo) > 0:
        return {"hit_boundary": True, "side": "below", "range": (tg_lo, None), "tg": None}
    lo, hi = tg_lo, tg_hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return {"hit_boundary": False, "side": None, "range": (tg_lo, tg_hi), "tg": (lo + hi) / 2}


def implied_irr(price, shares, fcf0, g1, tg=0.03, horizon=10, lo=0.0, hi=0.50, tol=0.001):
    """以现价买入基准情景现金流序列的隐含年化回报（IRR）。
    判读：IRR > WACC → 基准情景下现价有超额回报；IRR < WACC → 无安全边际。"""
    def f(w):
        return _dcf_value(g1, w, tg, fcf0, horizon) / shares - price
    if f(lo) < 0:   # 0%折现都覆盖不了现价 → 现金流在horizon+终值内永不回本
        return {"hit_boundary": True, "side": "below", "range": (lo, hi), "irr": None}
    if f(hi) > 0:
        return {"hit_boundary": True, "side": "above", "range": (lo, hi), "irr": None}
    lo_, hi_ = lo, hi
    while hi_ - lo_ > tol:
        mid = (lo_ + hi_) / 2
        if f(mid) < 0:      # f递减：折现率过高导致价值<现价 → 根在更低折现率
            hi_ = mid
        else:
            lo_ = mid
    return {"hit_boundary": False, "side": None, "range": (lo, hi), "irr": (lo_ + hi_) / 2}


def implied_sustainable_fcf(price, shares, net_cash, wacc, tg=0.03):
    """EV法：现价隐含的永续可持续FCF = EV×(WACC−g)/(1+g)。
    与实际正常化FCF对比：隐含 = 实际的X%（<100%=市场定价衰退/减速；>100%=已定价增长）。"""
    ev = price * shares - net_cash
    return ev * (wacc - tg) / (1 + tg)


def zero_growth_anchor(sustainable_fcf, wacc, net_cash=0.0, shares=1.0, wacc_range=None):
    """长期不增长情景（价值底线）：IV_zero = 可持续FCF/WACC + 净现金。
    现价÷锚 = 市场为"增长"支付的溢价倍数（博通：现价是零增长锚的3.3-4.0倍）。"""
    out = {
        "iv_zero": sustainable_fcf / wacc + net_cash,
        "per_share": (sustainable_fcf / wacc + net_cash) / shares,
    }
    if wacc_range:
        out["sensitivity"] = {w: (sustainable_fcf / w + net_cash) / shares for w in wacc_range}
    return out


def price_vs_scenarios(price, scenario_ivs):
    """现价 ↔ 情景IV对照与落点判读（反向DCF的核心输出）。
    scenario_ivs: {"悲观": iv, "基准": iv, "乐观": iv, "零增长锚": iv}（同单位：元/股）
    返回 [(名称, iv, vs现价%)...] + 落点判读语（六种标准语言之一）。"""
    rows = [(n, iv, (iv / price - 1) * 100) for n, iv in scenario_ivs.items()]
    ivs = dict(scenario_ivs)
    pessim, base, optim = ivs.get("悲观"), ivs.get("基准"), ivs.get("乐观")
    zero = ivs.get("零增长锚")
    if optim is not None and price > optim:
        verdict = "情境外：现价高于乐观情景IV——市场定价超出所有可推演情景，须用隐含g1语言重述（CAT：现价比乐观情景还高40%）"
    elif zero is not None and price < zero:
        verdict = "增长信仰归零：现价低于零增长锚——市场在为'麻烦'付费而非为增长付费（LULU）"
    elif pessim is not None and price <= pessim:
        verdict = "悲观侧定价：现价≈悲观IV——市场已按最坏情形定价，赔率不对称（ADBE）"
    elif base is not None and abs(price / base - 1) <= 0.05:
        verdict = "无安全边际：现价≈基准IV——市场按中性情景精确定价（TSM/WM）"
    elif base is not None and price < base:
        verdict = "基准与悲观之间：市场在打折，但未到悲观侧；关注隐含g1 vs 指引的缺口"
    else:
        verdict = "基准与乐观之间：市场已定价部分增长，安全边际为负"
    return rows, verdict


# === REVERSE DCF 输出（用 BASE PARAMETERS 演示；复用时填入正常化口径）=========
print(f"\n{'='*70}")
print("  反向DCF：当前股价隐含了什么增长预期？")
print("="*70)

sustainable_fcf = base_fcf   # ← 替换为正常化可持续FCF(亿)：收缩释放/一次性收益剔除后
net_cash = 0.0               # ← 净现金(亿，有息净负债为负)；EV = 市值 - 净现金
guidance_g = None            # ← 公司指引/一致预期增速(小数)；None则跳过对照行

# A. 隐含前10年FCF增速（其余参数锁定WACC/永续g）
r_g1 = implied_g1(price, shares, sustainable_fcf, WACC, terminal_g)
if r_g1["hit_boundary"]:
    lo, hi = r_g1["range"]
    lo_s = f"{lo*100:.0f}%" if lo is not None else "—"
    hi_s = f"{hi*100:.0f}%" if hi is not None else "—"
    print(f"  A. 隐含前10年FCF增速: 测试范围[{lo_s}, {hi_s}]外（{'低于' if r_g1['side']=='below' else '高于'}下/上界）")
    print("     → 报告边界条件，勿引用边界数值本身（EXPE隐含g1命中-10%下界即此读法）")
else:
    print(f"  A. 隐含前10年FCF增速: {r_g1['g1']*100:.1f}%/年")
    if guidance_g is not None:
        ratio = r_g1["g1"] / guidance_g if guidance_g > 0 else float("inf")
        print(f"     vs 指引/预期 {guidance_g*100:.1f}%: 倍数 {ratio:.1f}x（>2x=为'共识兑现但此后减速'付钱，TSM 21.5% vs 11%）")

# B. 隐含永续增长率（锁定g1=0.10演示；复用时用实际显性期增速）
r_tg = implied_tg(price, shares, sustainable_fcf, 0.10, WACC)
if r_tg["hit_boundary"]:
    print(f"  B. 隐含永续g: {r_tg['side']}测试上限 {r_tg['range'][1]*100:.1f}%（改报隐含g1或终值倍数）")
else:
    print(f"  B. 隐含永续g: {r_tg['tg']*100:.2f}%（显性期10%/年时）")

# C. 现价隐含IRR（以基准情景增速买入）
r_irr = implied_irr(price, shares, sustainable_fcf, 0.10, terminal_g)
if r_irr["hit_boundary"]:
    print(f"  C. 现价隐含IRR: 10年+终值现金流按0%折现也无法覆盖现价——现价隐含基准情景下永不回本")
else:
    edge = "高于WACC→基准情景有超额回报" if r_irr["irr"] > WACC else "低于WACC→基准情景无安全边际"
    print(f"  C. 现价隐含IRR(基准情景10%增速): {r_irr['irr']*100:.1f}%/年 vs WACC {WACC*100:.0f}% —— {edge}")

# D. 隐含可持续FCF（EV法）vs 实际
imp_fcf = implied_sustainable_fcf(price, shares, net_cash, WACC, terminal_g)
ratio = imp_fcf / sustainable_fcf if sustainable_fcf > 0 else float("nan")
print(f"  D. 现价隐含可持续FCF: {imp_fcf:.1f}亿 = 实际正常化FCF({sustainable_fcf:.1f}亿)的 {ratio*100:.0f}%")
print("     <100% = 市场定价减速/衰退；54-65%=市场按'整改后不可完全恢复'定价（携程）")

# E. 零增长锚（长期不增长情景）
anchor = zero_growth_anchor(sustainable_fcf, WACC, net_cash, shares, [0.08, WACC, 0.12])
print(f"  E. 零增长锚 IV_zero: {anchor['per_share']:.1f}元/股（FCF/WACC+净现金）")
print(f"     现价 {price:.2f} = 零增长锚的 {price/anchor['per_share']:.1f}倍 ← 市场为增长支付的溢价")
print("     WACC敏感性: " + " | ".join(
    f"WACC{w*100:.0f}%→{v:.1f}元" for w, v in anchor["sensitivity"].items()))
print("     ⚠ 低WACC会让锚膨胀，引用锚时必须注明WACC口径")

# F. 现价 ↔ 情景落点判读（与三情景DCF输出联动）
ivs_for_verdict = dict(scenario_iv_ps)
ivs_for_verdict["零增长锚"] = anchor["per_share"]
rows_v, verdict = price_vs_scenarios(price, ivs_for_verdict)
print(f"\n  现价落点判读（六种标准语言之一，见 references/reverse-dcf-analysis.md）:")
for n, iv, up in rows_v:
    print(f"    {n}: IV={iv:>6.1f}元 ({up:>+4.0f}% vs 现价)")
print(f"  → 判读: {verdict}")
