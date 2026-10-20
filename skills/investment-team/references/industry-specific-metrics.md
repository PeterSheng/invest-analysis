# Industry-Specific Metrics & Analysis Patterns

Captures industry-specific data points, modeling quirks, and analysis angles discovered across multiple company analyses.

---

## Semiconductors (台积电 TSMC 类型)

### ⚠️ 数据验证陷阱（本会话经验）

台积电分析中数据被修正了两次，核心问题：

1. **ADR/台股价格校验**：台积电1 ADR = 5普通股, 汇率~32 TWD/USD。验证公式：`ADR价格 × 32 ÷ 5 ≈ 台股价格`。第一次分析用了过期数据（ADR $215 / 台股 NT$1,380），第二次修正仍偏低（ADR $242 / 台股 NT$1,550），用户指出实时价格为NT$2,290；2026-10 重析轮第四档：ADR $422.25 ↔ 台股 NT$2,733（×32.36÷5 反推吻合）。**教训：对高波动股票，必须从最新财报新闻中确认当前价格，而非依赖上一季度的数据；ADR 比率反推（ADR×汇率÷5）是零成本的双源验证。**

2. **CapEx是"移动靶"**：Q2 2026财报同时宣布CapEx从$52-56B上调至$60-64B（+$8B, +15%）。这个变化在最初的搜索中被遗漏，直到Bloomberg 7/17报道"芯片股因CapEx上调而抛售"才被发现。**教训：财报新闻中除了EPS和营收，必须显式搜索CapEx/guidance update。**

### ⚠️ 盈利爆发摊薄 PE 的估值幻觉（2026-10 重析轮核心教训）

TTM PE 从 37.5x（2026-07，$358）"降"到 28.0x（2026-10，$422.25），表面是估值消化，实际是净利 +71% 摊薄分母的纯算术效应——同期 PB 创历史最高 10.06x、FCF Yield 2.09%（对 10Y 美债负利差 -2.1pp）。**盈利爆发期 PE 跨期对比失效，「PE 降了=变便宜了」是幻觉；必须并看 PB/FCF Yield/EV-EBITDA 判断实际贵贱。** 同族模式：苹果 ROE 190%/PB 74x（回购压缩权益）、英伟达 PE/ROE 0.31（周期顶部利润）——高倍数公司的单一倍数跨期对比全部失真，每类公司须选对"不失真的那一对"。

快捷量化「市场在定价什么」=现价反推隐含 g1：台积电 21.5%/年 ≈ 当年实际增速（Q4 YoY +58%）→ 市场按「高增长再续 5 年零差错」定价，任何一次「仅仅是很好」的季度都是回撤触发器。

### Must-Collect Data
| Metric | Why | Example |
|--------|-----|---------|
| **毛利率 by quarter** | 核心盈利质量指标，体现定价权和良率 | Q2'26 68.5% vs FY2022 59.6% |
| **净利率趋势** | 营业杠杆系数 = NI增长 ÷ 营收增长 | TSMC Q2'26: 77.4%/36.0% = 2.15x |
| **HPC/AI 收入占比** | AI需求的直接暴露度 | TSMC: 66% of revenue |
| **CapEx & CapEx/营收比** | 资本密集度趋势，影响FCF判断。**财报后必须确认是否更新** | TSMC 2026E: $60-64B (从$52-56B上调), ~41% ratio |
| **CapEx guidance change** | ⚠️ 财报常伴随CapEx调整，直接影响FCF和估值 | TSMC Q2上调$8B → FCF减少24% |
| **先进制程产出比 (3nm/5nm/7nm)** | 技术领先性的量化 | ~90% of ≤7nm chips |
| **FCF率** | CapEx吞噬多少OCF | TSMC: 25.6% in 2025 |
| **先进制程良率 vs 竞品** | 技术领先性从叙事变数字 | 2nm: TSMC 70-80% vs Samsung 40-55% vs Intel 18A 10-30%（传闻） |
| **需求侧领先指标（AI capex 依赖型）** | 客户景气先于自身财报暴雷 | OpenAI 年化营收 vs 传闻口径（10/8 $50B vs $70B → AI 链 NVDA -3%/ORCL -5.5% 集体重挫）；**跟踪第一行=次年 1-2 月云厂 capex 指引** |

### Modeling Quirks
- **TWD↔USD conversion**: 1 ADR = 5 common shares. TWD data in reports, convert to USD for DCF.
- **DuPont sensitivity**: TSMC has very low financial leverage (equity multiplier ~1.6x) — ROE is almost entirely driven by net margin. DuPont ROE may not match reported ROE due to approximate balance sheet; focus on margin *direction* not absolute precision.
- **DCF approach**: FCFE model with CapEx as the key variable. During heavy capex cycles, FCFE DCF will show undervaluation — complement with PE-based terminal value.
- **Geopolitical discount**: Always include Taiwan Strait risk in the risk analysis. It's the single largest tail risk.

### Report Angles
- **段永平**: "给你$5000亿能再造一个吗?" — the time + process-knowledge moat
- **巴菲特**: Margin expansion story + CapEx ROI question
- **芒格**: Taiwan Strait tail risk + 55% net margin attracts competition
- **李录**: "人类计算文明的物理载体" — civilization-level thesis

### 重析轮档案（2026-10-16，reports/202610/台积电/）

首轮 2026-07 综合 3.94 → 本轮 **3.38**（段 4.25/巴 3.00/芒 3.00/李 3.25，四分均落预判锚 ±0.25 内）。李录锚定硬规则（FCF Yield < 无风险利率 → 锚 ≤3.25）首次实战触发且被子报告零偏差确认（文明赛道 5 星 × 价格 1.5 星）。跟踪第一行：①2027 年 1-2 月云厂 capex 指引（集体下调 → 悲观情景概率 30%→50%）；②OpenAI/Anthropic 收入轨迹；③2nm 良率与 CoWoS 排单；④对台关税落地形态（100% 全额 vs 美国产能豁免）。

---

## Investment Banks (高盛 GS 类型)

### Must-Collect Data
| Metric | Why | Example |
|--------|-----|---------|
| **ROTE** (not just ROE) | Primary profitability metric for banks | Q2'26: 25.5% |
| **P/TBV** (not just P/B) | Primary valuation multiple | 2.67x |
| **Equity multiplier** | Leverage risk indicator | 13.3x for GS |
| **Trading revenue breakdown** | Equities vs FICC, cyclicality signal | Equities +72% YoY |
| **Segment revenue split** | GBM vs AWM vs Platform Solutions | 65/30/5 |
| **ROE sensitivity table** | Show valuation at different ROE assumptions | ROE 23.5%→18%→14%→10% |

### Modeling Quirks
- **OCF/NI < 1.0 is normal**: Banks' OCF includes trading asset changes, so OCF/NI of 75-82% is fine.
- **P/B ← ROE mapping**: Use implied P/B = ROE / Ke instead of DCF. Bank DCF is unreliable.
- **ROTE > ROE typically**: Due to goodwill exclusion. The gap quantifies acquisition premium.
- **Segment modeling**: GBM is cyclical (trading + IB fees), AWM is sticky (management fees), Platform Solutions is small but growing.

### Report Angles
- **段永平**: Brand + talent moat, but "can you predict next quarter?" test
- **巴菲特**: ROE cycle analysis — "23.5% ROE is a curse, not a feature"
- **芒格**: "You're betting on no market correction for 3-5 years"
- **李录**: Capital markets are civilization-level, but AI is compressing the "information asymmetry" moat

---

## Fintech / Payments (PayPal PYPL 类型)

### Must-Collect Data
| Metric | Why | Example |
|--------|-----|---------|
| **Take Rate** | THE critical metric — revenue/TPV | PYPL: 2.02%→1.87%, compressing 3-7bps/yr |
| **TPV growth vs Revenue growth** | Take Rate compression signal | TPV +7.2% but rev +5.3% |
| **Active accounts** | Network effect health | 439M, but growth stalling |
| **FCF/NI ratio** | Platform companies often FCF > NI | PYPL: 112% (payment float benefit) |
| **Venmo monetization** | Key growth vector | $1.4B rev → target $2B by 2027 |
| **Competitor TPV comparison** | Relative market position | Stripe $1.9T has surpassed PYPL $1.79T |

### Modeling Quirks
- **Take Rate trajectory is everything**: Model 3 scenarios for where Take Rate bottoms (1.8%, 1.5%, 1.2%) — this determines the entire valuation range.
- **FCF can exceed NI significantly**: Payment companies hold customer funds (float), so OCF > NI is normal.
- **TPV is the "top of funnel"**: Revenue = TPV × Take Rate. Model both separately.
- **Per-account metrics**: Revenue per active account = revenue / accounts. PYPL: $76.3 per account.

### Report Angles
- **段永平**: "Can you raise prices without losing customers?" → Take Rate says NO
- **巴菲特**: 8x PE + 16% FCF yield is mouth-watering but "value trap or bargain?"
- **芒格**: Take Rate "death by a thousand cuts" is the most certain risk
- **李录**: Digital payments = civilization-level, but "embedded finance" shifts power from PayPal to Stripe

---

## Event-Driven Supplementary Analysis

When the user asks about a specific corporate event (M&A bid, spin-off, activist campaign) alongside the standard four-master analysis, add a **fifth report**: `05-{事件名称}专项分析.md`.

### Structure for event analysis
1. **交易概要**: Parties, price, premium, financing, timeline
2. **战略逻辑**: Why the deal makes sense (or doesn't)
3. **价格分析**: Is the offer fair? (use DCF range + comparable transactions)
4. **成功概率评估**: ~7 factors with individual probabilities, weighted average
5. **四大师看法**: How each master would view the deal
6. **投资者操作指南**: What to do if holding/wanting to buy

### Example: Stripe+Advent bid for PayPal
- 75% strategic fit, 70% financing feasibility, 55% price adequacy, 40% antitrust
- Weighted success probability: ~50%
- Added as `05-Stripe收购专项分析.md`
