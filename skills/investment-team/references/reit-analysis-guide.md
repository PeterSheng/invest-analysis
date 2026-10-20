# REIT Analysis Guide (for Buffett-Style Valuation)

> Battle-tested on Lamar Advertising (LAMR) 2026-06-24. For US REITs analyzed from SEC EDGAR data.

## Key Differences from Standard Companies

REITs（房地产投资信托）的财务报表结构与普通公司有本质区别，需要完全不同的分析框架：

| Dimension | Standard Company | REIT |
|:---|:---|:---|
| Primary earnings metric | EPS / Net Income | **FFO / AFFO** |
| Valuation multiple | PE ratio | **P/FFO, P/AFFO** |
| D&A treatment | Non-cash expense | **Add back to compute FFO** (REIT depreciation is massive) |
| Dividend payout | From earnings | **90%+ of taxable income required by law** |
| Growth funding | Retained earnings | External (debt/equity issuance) |
| DCF WACC | 10-12% | **8%** (more stable cash flows) |

## FFO and AFFO Computation

### FFO (Funds From Operations)
```
FFO = Net Income + Depreciation & Amortization − Gains on Sale of Property + Impairments
```
Simplified (when gains/impairments are immaterial):
```
FFO ≈ Net Income + DepreciationAmortizationAndAccretionNet
```

### AFFO (Adjusted Funds From Operations)
```
AFFO = FFO − Maintenance Capital Expenditures − Straight-Line Rent Adjustments
```
Simplified:
```
AFFO ≈ FFO − Total CapEx (when maintenance ≈ total for stable REITs)
```

## SEC EDGAR XBRL Tags for REITs

### Critical Tags
| XBRL Tag | Purpose | Notes |
|:---|:---|:---|
| `RevenueFromContractWithCustomerIncludingAssessedTax` | Revenue | Same tag as non-REIT companies |
| `NetIncomeLoss` | Net Income | Starting point for FFO |
| `DepreciationAmortizationAndAccretionNet` | Total D&A | **KEY**: add back to NI for FFO |
| `AmortizationOfIntangibleAssets` | Intangible amortization | Included in above, but can check separately |
| `PaymentsToAcquirePropertyPlantAndEquipment` | CapEx | Deduct from FFO for AFFO |
| `NetCashProvidedByUsedInOperatingActivities` | Operating CF | Cross-check for cash quality |
| `LongTermDebtNoncurrent` | Long-term debt | REITs typically carry significant debt |
| `StockholdersEquity` | Book equity | Less meaningful for REITs (high depreciation) |
| `Assets` | Total assets | Cross-check debt/asset ratio |

### Tags Often Missing for REITs
- `EarningsPerShareDiluted` — may not be filed or may be unreliable
- `GrossProfit` / `CostOfGoodsAndServicesSold` — REITs don't use these categories
- `EntityCommonStockSharesOutstanding` — may not appear in DEI; compute from market cap ÷ price

## Valuation Framework

### AFFO-Based DCF (Preferred)
```python
wacc = 0.08  # lower for REITs
terminal_growth = 0.02  # or 0% for declining industries

for year in projection_years:
    affo_ps = current_affo * (1 + growth_rate) ** year
    pv += affo_ps / (1 + wacc) ** year

terminal_value = last_year_affo * terminal_p_affo / (1 + wacc) ** years
```

### Terminal P/AFFO Multiples by REIT Type
| REIT Type | Bear | Base | Bull |
|:---|:---:|:---:|:---:|
| Data center (EQIX/DLR) | 15-17x | 20-23x | 25-28x |
| Outdoor advertising | 12-15x | 16-19x | 20-22x |
| Industrial/logistics | 15-18x | 19-23x | 24-28x |
| Retail | 10-13x | 14-17x | 18-20x |
| Office | 8-12x | 13-16x | 17-20x |
| Residential | 14-17x | 18-22x | 23-26x |

### Dividend Analysis for REITs
- EPS < DPS is NORMAL for REITs — depreciation is non-cash
- Payout should be computed from AFFO, not EPS: `DPS / AFFO_per_share`
- Healthy range: 70-85% of AFFO
- > 90% of AFFO = dividend at risk if AFFO declines
- Compute DDM with AFFO growth rate (not EPS growth)

## Common Pitfalls

1. **Don't use PE for REITs**: A REIT with PE 28x may actually be cheap on P/AFFO 16x. The depreciation distortion is massive.

2. **Don't panic at high debt**: REITs typically carry 40-55% debt/asset ratios. This is structurally normal — they're asset-heavy, cash-flow-stable businesses. Check interest coverage (FFO/interest expense > 3x).

3. **EPS < DPS is normal**: A REIT paying $6.30 dividend on $5.42 EPS is healthy if AFFO is $7.21 (87% payout). Don't flag this as a red flag.

4. **Revenue tags may be sparse**: Some REITs file revenue under non-standard tags. Always search for 'revenue' across all us-gaap tags. `RevenueFromContractWithCustomerIncludingAssessedTax` is the most common modern tag.

5. **Shares outstanding may be missing from DEI**: Use market cap ÷ price to verify, then use the resulting share count consistently.

## Lamar (LAMR) Quick Reference

- CIK: 0001090425
- Type: Outdoor Advertising REIT
- Key XBRL tags verified:
  - Revenue: `RevenueFromContractWithCustomerIncludingAssessedTax` FY2025 = $2,266M
  - D&A: `DepreciationAmortizationAndAccretionNet` FY2025 = $326M
  - Intangible Amort: `AmortizationOfIntangibleAssets` FY2025 = $144M
  - CapEx: `PaymentsToAcquirePropertyPlantAndEquipment` FY2025 = $181M
- FY2025: **AFFO/Share $8.26**（AFFO 总额 $846.7M）, P/AFFO 14.99x（FY2025 年末价 $123.77）, Dividend $6.20 (75% payout)
  - ⚠️ **2026-06 首轮报告误用 AFFO/股 $7.21 → 把 P/AFFO 报成 21.1x（实际 18.4x），高估估值约 15%。** 教训：AFFO 一定要用「公司披露的全年稀释 AFFO/股」或「AFFO 总额 ÷ 稀释股本」核对，不要从第三方聚合器抄。
- Peer: Outfront (OUT) P/AFFO 15.5x, Clear Channel (CCO) 12x
- Key moat: Billboard permits grandfathered under Highway Beautification Act (1965) — cannot build new ones

---

## ★ Lamar (LAMR) 实测数据包（2026-09-18 第二轮验证，可直接复用）

| 指标 | 数值 |
|:---|:---|
| AFFO/股 | 2022 $7.45 → 2023 $7.47 → 2024 $7.99(+7.0%) → 2025 **$8.26**(+3.4%) → **2026E 指引 $8.75–8.90**（中值 +6.8%）；CAGR(23→26E) 5.8% |
| 现价 $146.81（2026-09-17）| **P/AFFO 16.6x（FY26E 中值）/ 17.8x（FY25）** ｜ P/FFO 15.5x ｜ AFFO 收益率 **6.01%** ｜ 股息率 4.50% ｜ 派息率占 AFFO **74.8%** |
| 有息债务 | **$3.514B**（WA 利率 4.5%，无 2028-02 前到期）｜ **租赁负债另计 $1.464B**（广告牌地租） |
| 净债/调整后 EBITDA | 公司口径 **2.9x** ｜ **含租赁 4.2x**（利息保障 7.1x）—— **报告必须以含租赁为主锚** |
| EV/EBITDA FY2026E | 15.6x（不含租赁）｜ **16.9x（含租赁）** |
| ROE / ROA / ROIC | **59.43%（失真禁用，权益仅 $982M）/ 6.60% / 11.89%** |
| 2026Q2 | 营收 $616.7M(+6.5%)、收购调整后 **+6.1%**、调整后 EBITDA $303.4M(+9.0%)、**利润率 49.2%（+110bp 历史新高）**、AFFO/股 $2.40(+8.1%) |
| 数字/程序化 | 数字屏 **5,730 块**、数字广告牌收入 **+15.4%**、占广告牌收入 **33.3%**；程序化 **+50%+**，仅占数字收入 **10%** |
| 护城河 | **1965 年《公路美化法》祖父条款 → 新建广告牌许可几乎不可能**；362,000+ 展示位；本地/区域占广告牌收入 78%（连续 21 季增长） |

### ★ 新增方法一：同业并购倍数交叉验证（REIT/OOH 专用）

**单看 DCF 会得出"低估"，单看同业倍数会得出"高估"——两者必须并列呈现。**
配方：`(同业 EV/EBITDA 倍数 × 公司 EBITDA − 公司净债务) ÷ 股本 = 隐含股价`。

Lamar 实测（FY2026E 调整后 EBITDA $1,176M、净债务公司口径 $3.446B）：

| 对标倍数 | 隐含股价 | vs 现价 |
|:---|:---:|:---:|
| Clear Channel 被 Mubadala 私有化 **11x**（$2.43/股，较未受影响价溢价 71%，EV 约 $62 亿） | $93 | **−36%** |
| 行业 2026E EBITDA 中位数（Solomon Partners 2026-09）**11x** | $93 | **−36%** |
| OUTFRONT **13.2x** | $119 | −19% |
| Lamar 当前 **15.6x** | $147 | 0% |

> ⚠️ **反直觉但关键的结论**：**"被收购期权"对优质龙头是下行锚而非上行期权**——按行业清算价卖掉反而亏 19–36%，因为质量溢价已经全额反映在价格里。**不要看到同业被高价收购就假设自己是下一个受益者。**
> 溢价的合理性论证要回到利润率断层（Lamar 调整后 EBITDA 利润率 **49.2%** vs OUTFRONT 约 **31%**——后者大比例收入来自与交通机构分成的低毛利交通媒体）。

### ★ 新增方法二：多重扩张检验（所有"长期上涨的优质资产"必做）

把总回报拆成「每股指标增长」与「估值倍数变动」两部分，判断"便宜"是否已被历史行情用掉。

Lamar 实测：**FY2022 末 $79.30 → 2026-09-17 $146.81 ＝ +85%，其中 AFFO/股仅 +18%、估值倍数 +56%（P/AFFO 10.65x → 16.6x）＝ 约 2/3 以上回报来自重估而非增长。**
配方：
```
倍数扩张贡献 = (P1/E1) ÷ (P0/E0) − 1
每股指标贡献 = E1 ÷ E0 − 1
```
结论语言：**"未来的回报必须由每股指标增长 + 股息承担，不能再指望重估"**，并据此反推三年/十年可实现回报（Lamar：三年年化 7.5%–9.4%、十年 IRR 11.0%）。

### ★ 新增方法三：现价反推三连问（REIT 版）

固定 DCF 的两个参数，反推第三个，三个问题一起问：
1. **WACC 8% / 终值 P/AFFO 16x 下，现价隐含的前 10 年 AFFO 增速是多少？**（Lamar：**2.16%**，而指引 +6.8%、历史 CAGR 5.8%）
2. **WACC 8% / g 5% 下，现价隐含的终值 P/AFFO 是多少？**（Lamar：**10.7x**，低于同业中位数 11x）
3. **AFFO g 5% / 终值 16x 下，现价隐含的要求回报（IRR）是多少？**（Lamar：**11.0%**）

> 三个数字合起来才能判断"市场是否已按最坏情形定价"——只看一个容易得出片面结论。

### ★ 新增方法四：租赁负债的口径问题（所有重资产 REIT）

必须做**双口径并列**：`公司口径净债/EBITDA` vs `含租赁负债净债/EBITDA`（Lamar：2.9x vs 4.2x；EV/EBITDA 15.6x vs 16.9x）。
- 公司口径通常排除经营租赁负债，看起来更漂亮；
- 租赁负债（如广告牌地租、门店租金）是**真实、逐年递增的合同义务**；
- **报告应主张以含租赁口径为主锚，并在排名表/对标表中同时标注两个数字。**

### REIT 排名表换锚规则

| 禁用 | 改用 |
|:---|:---|
| PE（折旧失真，Lamar 26.81x 无意义） | **P/AFFO、P/FFO** |
| ROE（负权益/微权益致失真，Lamar 59.43%） | **ROIC、ROA** |
| PB（资产账面已被累计折旧压低） | **EV/EBITDA、AFFO 收益率** |

---

## ★ Equinix (EQIX) 实测数据包（2026-10-11，可直接复用）

| 指标 | 数值 |
|:---|:---|
| AFFO/股 | 2021 $29.60† → 2022 $31.40† → 2023 $32.30† → 2024 $35.00 → 2025 **$38.33**(+9.5%) → **2026E 指引 $42.69-43.29**（中值 +12.2%）；CAGR(21→26E) 7.7% |
| 现价 $1,026.06（2026-10-09）| **P/AFFO 23.9x（26E）/ 26.8x（FY25）** ｜ AFFO 收益率 **4.19%** ｜ 股息率 2.01%（$20.64/年，连续 11 年提息）｜ **派息率仅 48% of AFFO**（REIT 罕见成长型结构，留存 52% 再投资）|
| 有息债务 | $23.36B（含融资租赁）｜ 净债 $22.38B ｜ **净债/EBITDA 双口径：公司口径 3.6x（年化调整后 EBITDA）vs 自算 ~4.0x（Q2'26 年化 $5.6B）** |
| EV/EBITDA | 27.3x（TTM）/ 22.8x（26E fwd）｜ ROIC 5.61% < WACC 8.5%（投资期拖累）｜ TTM OCF $3.9B vs CapEx $6.5B = **FCF 缺口 -$2.6B/年** |
| 数据中心同业 | DLR P/core-FFO 23.0x（$188.39 / core FFO $8.15-8.20）、IRM ~19x、O ~14.5x；私募 cap rate 5.5-6.5% → 隐含 P/NOI 15-18x；EQIX 历史中枢 ~22x（2021 泡沫 30.1x → 五年倍数收缩 -21%）|
| 护城河 | 互连生态网络效应（10,000+ 客户/77 都市，零售互连近乎垄断）+ 中立性（不与客户竞争）；Q2'26 净新增互连 9,700 创纪录、60% 大单 AI 驱动 |
| 指引弧线 | 2025-06 分析日因 capex 拖累**下调**长期 AFFO 增速至 5-9%（股价当日大跌）→ 2026-07 Q2 财报**上调回 9-12%**（+营收 10-13%/年至 2029）——"分析日下调 → 季报上调"是 REIT capex 周期的典型信号对 |
| 做空/诉讼 | Hindenburg 2024-03-20：维护 CapEx 误分类为增长 CapEx → 虚增 AFFO 20%+、高管薪酬挂钩 AFFO；集体诉讼获准推进 + 2025 第二起；若指控成立真实 P/AFFO ≈ 28.7x |

†2021-2023 为多源拼接（±$1）。

### ★ REIT 版"现价反推三连问"的二分方向陷阱（EQIX 2026-10 实测）

反解三个隐含参数时，目标函数随参数的**单调方向不同**，二分法方向必须逐个确认，**解出后必须正向回代验证 PV≈现价**：

| 问题 | 目标函数单调性 | EQIX 实测解 |
|:---|:---|---:|
| ① WACC/终值固定 → 隐含 10 年 AFFO 增速 | 递增（g↑→PV↑） | **5.6%**（指引 9-12%，市场只信一半）|
| ② WACC/g 固定 → 隐含终值 P/AFFO | 递增（倍数↑→PV↑） | **13.5x**（历史中枢 22x，定价终局去化）|
| ③ g/终值固定 → 隐含要求回报（IRR） | **递减（WACC↑→PV↓）→ 二分方向与①②相反** | **11.7%**（> REIT 要求回报 8-8.5%）|

实测教训：③ 若沿用①②的 `if fv < price: lo = mid` 会收敛到 3.0%（方向反了），③ 正确逻辑是 `if fv > price: lo = midw`。三问合读 = "现价 = 只兑现一半增速"或"终值砍到 13.5x"；若指引全兑现则 IRR 11.7% 有安全边际——**只看单问会得出片面结论**（与 Lamar 三连问同构）。
