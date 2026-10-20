# Financial Institutions Modeling (Banks, Investment Banks, Asset Managers)

Use this instead of the generic `dupont_analysis.py` template when analyzing:
- Investment banks (Goldman Sachs, Morgan Stanley)
- Commercial banks (JPMorgan, Bank of America)
- Asset managers (BlackRock, Blackstone — partially)
- Insurance companies (use `insurance-modeling.md` instead)

## Why Separate Modeling?

Financial institutions are fundamentally different from operating companies:
- **"Assets" are financial instruments**, not PP&E — asset turnover is meaningless as an efficiency metric
- **Debt is raw material**, not leverage in the corporate sense — the equity multiplier IS the leverage
- **Cash flow is unreliable** — trading assets/liabilities mark-to-market swings make OCF volatile
- **Book value matters** — unlike a factory, financial assets are marked to market, so BV is more meaningful
- **ROE is cyclical by nature** — mean reversion is the dominant force

## Core Metrics

### 1. ROE via DuPont (Special Interpretation)

```
ROE = Net Margin × Asset Turnover × Equity Multiplier
```

| Component | Non-Financial Interpretation | FI Interpretation |
|-----------|----------------------------|-------------------|
| **Net Margin** | Operating efficiency | Profitability of financial activities (trading, advisory, lending) |
| **Asset Turnover** | Capital efficiency | Revenue generated per $ of financial assets |
| **Equity Multiplier** | Financial leverage | **THE** key risk metric — Total Assets / Equity |

**What matters:** For FIs, the equity multiplier IS the leverage story. A rising equity multiplier means the firm is taking more risk. Even if ROE looks great, if it's driven by leverage expansion (not margin improvement), it's a "bad rise."

**Diagnosis rule:**
- ROE ↑ driven by Net Margin ↑ → **"Good rise"** (quality improvement)
- ROE ↑ driven by Equity Multiplier ↑ → **"Bad rise"** (more leverage, hidden risk)
- Need both margin AND multiplier trend to judge

### 2. ROTE (Return on Tangible Equity)

```
ROTE = Net Income / (Shareholder Equity - Goodwill - Intangibles)
     = Net Income / Tangible Common Equity
```

**Always compute ROTE alongside ROE.** If ROTE >> ROE, the firm has significant goodwill (from acquisitions). High goodwill + high leverage = fragile balance sheet.

For Goldman Sachs Q2 2026: ROTE 25.5% vs ROE 23.5% — modest gap, balance sheet quality is acceptable.

### 3. TBVPS (Tangible Book Value Per Share)

```
TBVPS = Tangible Common Equity / Shares Outstanding
```

**P/TBV is the primary valuation multiple for financial institutions**, not P/B or P/E alone. TBVPS growth rate is the best proxy for intrinsic value growth in FIs.

### 4. Valuation Framework: ROE → P/B Mapping

For financial institutions, the Buffett-style valuation is:

```
Implied Fair P/B = ROE / Cost of Equity
```

| ROE | Ke=10% Fair P/B | Ke=12% Fair P/B |
|-----|:---------------:|:---------------:|
| 23.5% | 2.35x | 1.96x |
| 18% | 1.80x | 1.50x |
| 14% | 1.40x | 1.17x |
| 10% | 1.00x | 0.83x |

**Key insight:** Current high ROE supports high P/B — but only if ROE is sustainable. This is the central tension in FI valuation: the market ALWAYS prices cyclicals at peak ROE, and ALWAYS prices them at trough ROE. Your edge is in judging sustainability.

### 5. Normalized Earnings Framework

```
Normalized EPS = BVPS × Normalized ROE
Normalized Price = Normalized EPS × Normalized PE

Current Price / Normalized Price = Over/under-valuation ratio
```

Use 12-14% as normalized ROE for most investment banks (mid-cycle), and 10-12x as normalized PE.

### 6. OCF/NI for FIs

Unlike operating companies where OCF/NI > 1.0 is expected, for FIs:
- 0.75-0.85 is **normal** (trading assets/liabilities create non-cash P&L)
- < 0.6 is **concerning** (potential earnings quality issue)
- > 1.0 is **unusually strong** (may indicate asset liquidation)

### 7. Sensitivity Analysis (REQUIRED)

For any FI, build a sensitivity table:

| ROE Assumption | Fair P/B (@10% Ke) | Implied Price | vs Current |
|:--------------:|:------------------:|:------------:|:----------:|
| Current Peak | ROE / 0.10 | P/B × BVPS | — |
| Sustained High | High_ROE / 0.10 | ... | ... |
| Mid-Cycle | 0.14 / 0.10 = 1.40x | ... | ... |
| Recession | 0.10 / 0.10 = 1.00x | ... | ... |
| Crisis | 0.06 / 0.10 = 0.60x | ... | ... |

This table IS the analysis — it shows the range of outcomes and lets the reader judge which ROE scenario they believe in.

### 8. Online Brokers / Fintech Brokerages（FUTU 2026-08 实战）

互联网券商（富途/IBKR/Robinhood/老虎）介于传统券商与平台公司之间，五个特有处理：

| 特性 | 处理 |
|------|------|
| **OCF/NI 3-6x 是常态，不是盈利质量问题** | 客户资金进出（应付款项变动）主导 OCF（FUTU：FY2025 OCF HK$408亿 vs 净利 HK$113亿，OCF/NI 3.6x；FY2024 5.7x）。**OCF/FCF 不可用于估值**，别按常规"OCF/NI > 1 健康"检查表误判 |
| **资本开支接近零 = 盈利几乎全部可分配** | FUTU CapEx 仅营收的 0.03%——纯平台模式。分红+回购能力 = 净利的 75%+，payout 有巨大提升空间 |
| **净现金可能占市值 80%+** | FUTU 净现金 HK$1,084亿 = 市值 86%——资产负债表极稳，报告必须单列此项（这是估值的安全垫） |
| **正常化盈利：一次性监管罚款先剔除再比 PE** | FUTU：Q1'26 计提 CSRC RMB 18.5亿罚款 → TTM 净利 HK$111亿，剔罚款后 HK$131.5亿（+16% YoY），调整后 PE 9.6x vs 表面 11.55x。**罚款/诉讼/一次性收益对 TTM 的污染在券商监管事件中常见，必须做"剔除非经常项"TTM** |
| **两套框架分歧本身就是结论** | 当 PE-vs-历史（9.6x vs 15x 中枢 = 低估 33%）与 ROE→P/B 公平值（Ke10% → $110 vs 现价 $116 = 无安全边际）方向相反时，**分歧即分析**：市场在按"ROE 回归 + 监管折价"重新定价，现价站在两框架交界处。报告须并列表述，不强行收敛 |

**"ROE 是天气不是能力"诊断**（市场热度放大杠杆的券商必做）：
- DuPont 拆解看 ROE 构成：FUTU TTM ROE 30.5% = 净利率 46.2% × 周转 0.082 × 权益乘数 7.46x——净利率 46% 是牛市净利率（历史熊市 40-42%），乘数 7.46x 是客户融资余额 +85% YoY 催肥的被动杠杆
- 必做 ROE 回归敏感性表：30%→3.05x / 25%→2.50x / 20%→2.00x / 15%→1.50x（Ke=10%），PB_norm = ROE_norm/ROE_now × PB
- PE/ROE 排名表给 <1.0 时，先判断 ROE 是否"牛市天气"，否则 0.38 这类数字是统计假象

## What NOT to Do for FIs

| ❌ Don't | ✅ Do |
|----------|------|
| Run standard DCF with free cash flow | FCF is meaningless for banks; use residual income or ROE-P/B framework |
| Compare P/E to the broad market | Banks trade on P/B, not P/E; compare to own history and peers |
| Treat high ROE as a sign of quality | High ROE at a bank may = high risk-taking; check the equity multiplier |
| Use 15-20% Ke | Banks have lower cost of equity due to diversification; use 10-12% |
| Ignore the cycle | Every FI analysis must include a "what happens when the cycle turns" section |
| Use generic OCF analysis | OCF/NI < 1.0 is NORMAL for banks — don't flag it as a problem |

## Integration with the Four-Master Reports

- **巴菲特 section:** Use ROE→P/B framework instead of DCF; include sensitivity table; show normalized valuation
- **段永平 section:** Focus on franchise value (brand, talent network, client relationships) — these are the real "assets" of an FI
- **芒格 section:** Equity multiplier trend, hidden leverage, counterparty risk, regulatory risk are the primary failure paths
- **李录 section:** Financial intermediation as a "civilization-level" service; AI disruption to information asymmetry
