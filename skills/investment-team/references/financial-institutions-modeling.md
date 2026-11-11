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
Implied Fair P/B = ROE / Cost of Equity        # 零增长版，只有当"全部盈利分红、BVPS 不增长"时才严格成立
Implied Fair P/B = (ROTE - g) / (COE - g)      # 增长版（Gordon）——留存复利型银行必须用这个
Implied ROTE (反解) = P/B × (COE - g) + g      # 现价隐含的可持续回报率，用于"市场已经相信什么"
```

**零增长版的问题是系统性低估留存型银行**：payout 50%、留存撑 BVPS 年增 8% 的银行，用 `ROE/Ke` 得到的公允 P/B 会偏低 30-50%。凡是有实质留存复利（g ≥ 2%）的银行，一律用增长版，并在报告里把 g 的来源写清楚（名义 GDP / 存款+贷款增速 / 通胀）。详见 §10.2。

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
| **净现金必须剔除"客户代持现金"** | 🔴 **2026-11 富途重析轮纠正**：首轮曾写"FUTU 净现金 HK$1,084亿 = 市值 86%"，实为把**客户代持现金 135.8B**（`Cash held on behalf of clients`）计入自有现金——错把客户的钱当股东安全垫，安全边际被放大约 10 倍。正解：企业净现金 = 自有现金 18,381 + 短投 6,612 + 定存 195 − 借款 15,735 − 租赁 540 = **HK$8,913M（市值 8.5%）**。券商客户资金同时是**利息收入的来源（盈利资产）**，不能与股东现金混算；且自有现金还受监管净资本锁定。任何券商净现金项都必须单列"自有 vs 代持"两行 |
| **正常化盈利：一次性监管罚款先剔除再比 PE** | FUTU：Q1'26 计提 CSRC RMB 18.5亿罚款 → TTM 净利 HK$111亿，剔罚款后 HK$131.5亿（+16% YoY），调整后 PE 9.6x vs 表面 11.55x。**罚款/诉讼/一次性收益对 TTM 的污染在券商监管事件中常见，必须做"剔除非经常项"TTM** |
| **两套框架分歧本身就是结论** | 当 PE-vs-历史（9.6x vs 15x 中枢 = 低估 33%）与 ROE→P/B 公平值（Ke10% → $110 vs 现价 $116 = 无安全边际）方向相反时，**分歧即分析**：市场在按"ROE 回归 + 监管折价"重新定价，现价站在两框架交界处。报告须并列表述，不强行收敛 |

**"ROE 是天气不是能力"诊断**（市场热度放大杠杆的券商必做）：
- DuPont 拆解看 ROE 构成：FUTU TTM ROE 30.5% = 净利率 46.2% × 周转 0.082 × 权益乘数 7.46x——净利率 46% 是牛市净利率（历史熊市 40-42%），乘数 7.46x 是客户融资余额 +85% YoY 催肥的被动杠杆
- 必做 ROE 回归敏感性表：30%→3.05x / 25%→2.50x / 20%→2.00x / 15%→1.50x（Ke=10%），PB_norm = ROE_norm/ROE_now × PB
- PE/ROE 排名表给 <1.0 时，先判断 ROE 是否"牛市天气"，否则 0.38 这类数字是统计假象

## 9. Commercial Banks: Three-Anchor Valuation Stack（招商银行 2026-10-20 实战）

商业银行（A/H 大行、股份行）的估值路径：**三锚并行 + 分歧即结论**，替代单点 FCF-DCF。三锚分歧的根源是**对留存收益的处理不同**——分歧本身就是分析对象，不是需要强行收敛的误差。

### 锚一：ROE→P/B 矩阵（无增长下限锚 + 危机格标定）

`公允 PB = ROE ÷ Ke`，× 最新中报 BVPS 得无增长公允价。敏感性按 ROE 情景 × Ke 区间铺满（招行示例）：

| ROE 情景 | Ke=9% | Ke=10% | Ke=11% |
|---|---|---|---|
| 持续 13.4% | 1.49x | 1.34x | 1.22x |
| 周期 11% | 1.22x | 1.10x | 1.00x |
| 保守 9% | 1.00x | 0.90x | 0.82x |
| 危机 8% | 0.89x | 0.80x | 0.73x |

**关键动作：危机格必须 ≈ 现价或历史最低点**（招行：ROE 8%×Ke 10% → 0.80x ≈ 现价 0.79x——"市场按危机格定价"是最干净的错杀证据）。若危机格仍显著高于现价，说明市场定价比危机更悲观，先查资产质量是否藏着未暴露问题，而不是急着喊低估。

### 锚二：DPS 路径 DDM（增长率必须自洽）

payout 固定时 **DPS 增速 = EPS 增速 = ROE × (1−payout)**——别让 DDM 的 g 与 ROE/payout 假设打架（招行：payout 35%、g1 4% 递减至 tg 3.5%）。三情景（ROE 守住/缓降/周期回落）概率加权得 IV。DDM 只对现金股息折现，天然低估留存收益 → 结果通常低于锚一。

### 锚三：剩余收益 RI（对留存收益最慷慨）

`V0 = BVPS0 + Σ RI_t/(1+Ke)^t`，`RI_t = (ROE_t − Ke) × BVPS_{t-1}`，BVPS 按 payout 累积。RI 把全部留存按超额回报复利计算 → 通常最高；**终值假设（ROE 长期贴 Ke）越乐观 RI 越虚高，须标注乐观偏置**。

### 三锚分歧 =「PB<1 时留存收益是否毁价值」的量化

招行实测：锚一危机格 42.9 元 / 锚二加权 38.7 / 锚三 ~49.7。**跨度本身写入结论**：payout 35% + PB 0.79x 时，每 1 元留存按 0.79 元市价变现——留存是否创造价值取决于再投资回报 vs Ke。**最高杠杆变量 = 派息率**：CET1 冗余近 6pct 的大行把 payout 提到 40%+，是管理层证明"留存不毁价值"的最便宜方式（招行 ~300 亿/年增量分红）。

### 现价反推三件套（银行版反向 DCF）

1. **隐含长期 ROE**：解 `P = BVPS × ROE_implied ÷ Ke`（招行：7.9-8.7% vs 实际加权 13.44% → 市场把零售之王按危机后普通股份行定价）
2. **零增长锚**：`DPS ÷ Ke`（股息率下限检验）
3. **TBVPS 复利年化回报**：exit PB 不变假设下，`年化 ≈ ROE×(1−payout) 留存复利 + 股息率`（招行：ROE 守 11% → 年化 ~12%；ROE 滑 9% → ~8%）——把"等周期反转"翻译成持有期回报预期

### 商业银行数据纪律

| 数据点 | 处理 |
|---|---|
| **加权 ROE** | 用公司披露的加权平均 ROE，勿用期末净利/期末净资产（利润留存使两者差 1-2pct） |
| **PB/PE 自算** | 腾讯行情 PE/PB 字段不可信（A+H 混合口径），用 `现价 ÷ 最新中报 BVPS/EPS` 自算 |
| **拨备覆盖率趋势** | 连续多年下行 = 利润反哺油箱见尾段 → **营收拐点比净利增速更重要**（招行 483.9%→385.1% 六连降，2026H1 营收 +4.83% > 净利 +2.02% 是健康信号） |
| **零售/对公不良双轨** | 零售不良拐点是估值胜负手（引管理层原话），对公/零售分开跟踪；综合裁决的 Follow-up 必须指向它 |
| **CET1 冗余** | 实际 CET1 − 监管底线 = 派息提升/回购的理论空间，巴菲特与芒格的共同变量 |
| **AUM 护城河本体** | 零售客户数/AUM/存款成本（活期+对公存款占比）——段永平视角的核心证据 |
| **AH 溢价** | H 溢价（南向资金集中）在 A/H 报价中并标，混合市值 = A股股数×A价 + H股股数×H价×汇率，勿用单边价格反推总市值 |

**综合裁决定锚**：公允区间 = 三锚跨度 + 同业 PB 分位（招行 0.79x vs 股份行 0.5-0.7x），击球区在区间下沿再留安全边际（招行：38-40 分批 / 33-35 重仓）。

## 10. G-SIB / 国际银行（多币种 + AT1 + 回购返还）—— 汇丰控股 2026-11 实战

适用于：汇丰、渣打、花旗、摩根、德银、UBS 等"多地上市 + 发 AT1 + 靠回购返还资本"的系统重要性银行。与 §9 的 A/H 大行差异在于：**资本结构里夹着 AT1、跨币种、回购是每股指标增长的主力**。

### 10.1 P/B 分母的三个口径（最容易犯且最致命的错）

| 口径 | 分母 | 汇丰 2026-11 实测 | 用途 |
|---|---|---:|---|
| **普通股股东权益** | 归属普通股股东的权益 | **1.73x** | ✅ **报告主口径** |
| 含 AT1/优先股的总权益 | 总权益（含 AT1、少数股东） | 1.51x（行情商口径） | ❌ 仅作对比，不可作结论 |
| TBV（剔商誉+无形） | 普通股权益 − 商誉 − 无形 | **1.86x** | 极端悲观/清算锚 |

- **行情商 PB 系统性低估**：AT1/优先股占总权益 10% 以上时，PB 被压 0.2-0.3x（汇丰 1.51 vs 真实 1.73，低估 13%）。腾讯行情、stockanalysis 的 PB 字段一律不引用，必须 `现价 ÷ 普通股权益 ÷ 股数` 自算，并在 `00-数据包.md` 写"三口径警示"小节。
- **PB 分母错 → 公允价错 → 击球区全错**。这是金融股报告里唯一会直接产生错误买卖建议的算术错误。
- 同一家银行 PB(普通股) < PB(TBV) 恒成立；若算出来反过来，说明有商誉为负或分母混了 AT1，立即复核。

### 10.2 增长版 P/B + 反解隐含 ROTE

```bash
python scripts/bank_valuation_pb.py --bvps 79.47 --tbvps 73.90 --price 137.50 \
    --rote 13,15.5,17.5 --coe 10.5 --g 3.5 --divps 6.1
```

- 公式：`公允 P/B = (ROTE − g)/(COE − g)`；`隐含 ROTE = P/B × (COE − g) + g`
- 汇丰实测：P/B 1.73 + COE 10.5% + g 3.5% → **隐含可持续 ROTE 15.6%**；而 3Q26 报告的 ROTE（含恒生私有化相关一次性收益）在 17%+，剔除一次性后接近 15-16% → **结论："市场定价 = 已默认 ROTE 从峰值回归到 15.6%，没有额外奖励"**。这一句比任何 PE 对比都锋利，务必写进巴菲特节与综合裁决。
- 桌面核对：把算出的公允 P/B 与公司自己披露的"目标 ROTE + 目标 CET1"对齐，如果两者矛盾，优先信公司的目标而不是你的 g。

### 10.3 资本返还（回购 + 股息）：G-SIB 估值的另一半

G-SIB 的每股 BVPS/EPS 增长有一大半来自**回购注销股数**，所以"回购是否可持续"必须单独建模，不能只算股息率。

| 变量 | 算法 | 汇丰实测要点 |
|---|---|---|
| CET1 缓冲 | 实际 CET1 − 监管/管理目标底线 | 14.x% vs 目标 ~10-11% → 缓冲 3-4pct |
| 缓冲的可返还金额 | 缓冲(bps) × RWA ÷ 10000 | 换算后除以股价 = 可回购股数占比 |
| **资本返还被打断** | 并购/私有化/监管加码吃掉缓冲 | 恒生私有化 −110bps → 暂停回购 |
| 情景必须单列 | "回购暂停 12 个月"格 | 回购是每股增长的引擎，停摆直接砍 P/B 溢价 |

**纪律**：三情景里的熊市情景不能只降 ROTE，必须同时写清"回购停 + 股息仅维持"，否则熊市价会系统性偏高。

### 10.4 一手数据：官方 earnings release PDF 优先于任何聚合库

聚合数据（akshare / 行情商 / 财经媒体）对港股国际银行的问题是**字段稀疏 + 口径混杂**（法定 vs 调整后、期间 vs 年化、含/不含一次性），而官方 release 一次给齐"调整后 ROTE + CET1 + 分部 PBT + 信贷成本 bps + 成本收入比"。

```bash
# 1) 从 IR 站 results 目录定位当季 PDF（国际银行多为同构路径：/investors/.../pdfs/...）
# 2) 转带版式文本（-layout 保留表格列对齐，否则数字和标签错位）
pdftotext -layout 3q26.pdf 3q26.txt
# 3) 按标签正则抓取（ROTE / CET1 / 净利息收入 / 预期信用损失 / 分部 PBT）
```

- 抓取顺序：**法定口径与调整后口径都要抓**，报告里并列表述并注明哪一套进了估值。
- 一次性项目（并购相关、出售收益、重组费用）必须在 ROTE 上做"剔除后再看"的双行，并在数据包标注金额。
- 分部利润表是段永平视角的核心证据（哪块业务在创造护城河），不要只用集团合计。

### 10.5 监管税负 = ROTE 的隐形折旧

英国 bank surcharge / 附加税率上调、以及各国"银行税"，直接打 ROTE 1-2pct 且不可逆。建模时**有效税率趋势单列一行**，别把当前 ROTE 当稳态；税率变化要在巴菲特节做"减税前后 ROTE 对照"。

### 10.6 多币种与 ADR 交叉校验

- **报价校验**：`HK 价 × 汇率` vs `ADR 价 ÷ 每 ADR 普通股数（汇丰 1:5）`，两条路径一致才认价格；差异 > 1% 先查汇率时点与 ADR 溢价。
- **分红口径**：股息率用"除净日口径"（港股除净日与派息日可差 1-2 个月），DDM 折现时点同理；用错口径会让股息率偏差 0.2-0.4pct，足以翻掉 HOLD/BUY 边界。
- 市值口径：多地上市必须按各地股数×当地价×汇率加总，不能用单边价格 × 总股本。

### 10.7 汇丰实测标定（仅供参照，勿照抄数字）

公允中枢 ROTE 15.5% × COE 10.5% → P/B 1.86x ≈ HK$148；熊 1.25x ≈ HK$99；牛 2.50x ≈ HK$199；现价 1.73x 无安全边际 → 综合 3.30/5、HOLD。**这个栈的价值不在结论，在于"现价隐含 ROTE"这一行把市场的假设显式化了。**

## What NOT to Do for FIs

| ❌ Don't | ✅ Do |
|----------|------|
| Run standard DCF with free cash flow | FCF is meaningless for banks; use residual income or ROE-P/B framework |
| Compare P/E to the broad market | Banks trade on P/B, not P/E; compare to own history and peers |
| Treat high ROE as a sign of quality | High ROE at a bank may = high risk-taking; check the equity multiplier |
| Use 15-20% Ke | Banks have lower cost of equity due to diversification; use 10-12% |
| Ignore the cycle | Every FI analysis must include a "what happens when the cycle turns" section |
| Use generic OCF analysis | OCF/NI < 1.0 is NORMAL for banks — don't flag it as a problem |
| Quote the PB printed by Tencent / stockanalysis | Self-compute `price ÷ common equity ÷ shares` — providers divide by total equity incl. AT1 and understate P/B by 0.2-0.3x (§10.1) |
| Value a retaining bank with `ROE / Ke` | Use `(ROTE − g) / (COE − g)`; the zero-growth form systematically under-prices banks that compound BVPS (§10.2) |
| Model the bear case as "lower ROTE" only | For G-SIBs the bear case must also say "buyback halted, dividend only" — buybacks are half the per-share growth engine (§10.3) |

## Integration with the Four-Master Reports

- **巴菲特 section:** Use ROE→P/B framework instead of DCF; include sensitivity table; show normalized valuation
- **段永平 section:** Focus on franchise value (brand, talent network, client relationships) — these are the real "assets" of an FI
- **芒格 section:** Equity multiplier trend, hidden leverage, counterparty risk, regulatory risk are the primary failure paths
- **李录 section:** Financial intermediation as a "civilization-level" service; AI disruption to information asymmetry
