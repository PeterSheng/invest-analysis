# Investment Income Contamination Detection

> When reported net profit growth looks good but may be masking core business deterioration. This pattern emerged from multiple Buffett-style analyses and is a reusable diagnostic framework.

## The Red Flags

Any ONE of these signals warrants deeper investigation:

| Signal | Example | What to Check |
|:---|:---|:---|
| **净利率 > 100%** | 九安2025: 净利率166% (22.67亿净利 > 13.66亿营收) | `invest_income` + `fair_changes_income` in benefit_new_ths |
| **净利增速 >> 营收增速** | 炜冈2025: 净利+47.5% vs 营收+9.4% | Discrepancy > 3x is suspicious |
| **经营现金流远小于净利润** | OCF/Net Profit ratio < 60% | Investment income doesn't generate cash flow |
| **ROE jumps without margin improvement** | — | Check if the jump is from financial income, not operational efficiency |

## Detection Formula (Quick Check)

```python
# After loading stock_financial_abstract_ths + benefit_new_ths:
net_profit = abstract_df['净利润']  # from abstract
invest_income = benefit_df['invest_income']  # from benefit_new_ths
fair_change = benefit_df['fair_changes_income']  # from benefit_new_ths

core_profit_approx = net_profit - invest_income - fair_change
contamination_ratio = (invest_income + fair_change) / net_profit

# If contamination_ratio > 30%: ⚠️ Profit is significantly investment-driven
# If contamination_ratio > 50%: 🔴 Core business may be unprofitable
# If contamination_ratio > 100%: 🔴🔴 Core business is LOSING money (九安2025)
```

## Real Examples (This Session)

### 九安医疗 (002432) — Contamination Ratio > 100%

| Year | Net Profit | Invest Income | Fair Value ∆ | Core Profit (est) | Core Running? |
|:---|:---|:---|:---|:---|:---|
| 2024 | 16.69亿 | 7.12亿 | 7.40亿 | ~2.17亿 | Barely |
| 2025 | 22.67亿 | 7.18亿 | 21.14亿 | **-5.65亿** | 🔴 LOSING |

### 炜冈科技 (001256) — Contamination Ratio 51%

| Year | Net Profit | Invest Income | Core Profit (est) | Real Growth |
|:---|:---|:---|:---|:---|
| 2024 | 0.90亿 | 0.17亿 | ~0.73亿 | — |
| 2025 | 1.33亿 | 0.69亿 | ~0.64亿 | **-12%** (vs reported +47.5%) |

### 杭氧股份 (002430) — Contamination Ratio Near Zero ✅

| Year | Net Profit | Invest Income | Fair Value ∆ | Core → Net |
|:---|:---|:---|:---|:---|
| 2025 | 9.49亿 | 0.15亿 | negligible | ✅ Pure operating |

### 永新股份 (002014) — Clean, Minimal Investment Income ✅

| Year | Net Profit | Invest Income | Core Profit | Ratio |
|:---|:---|:---|:---|:---|
| 2025 | 4.38亿 | 0.17亿 | ~4.21亿 | 3.9% ✅ |

### 大连电瓷 (002606) — Clean Operating Profit ✅

| Year | Net Profit | Invest Income | Fair Value ∆ | Ratio |
|:---|:---|:---|:---|:---|
| 2025 | 2.12亿 | 0.01亿 | negligible | 0.6% ✅ |

> **Spectrum summary**: 九安>100% (core losing money) → 炜冈 51% (half from investments) → 永新 4% (clean) → 杭氧/大连 <1% (pure industrial). The contamination ratio directly maps to Buffett's "can I predict future earnings?" test — the higher the ratio, the less predictable.

## How to Report It

When presenting in the analysis:

1. **Always show the breakdown table** (营收, 营业利润, 投资收益, 公允价值变动, 归母净利)
2. **Compute core profit estimate** and compare growth rates
3. **Flag the contamination ratio** prominently in the summary
4. **For the valuation section**, use core/operating profit (not reported net profit) as the basis
5. **In the Buffett rating**, downgrade "利润质量" when contamination > 30%

## Data Source

Use `stock_financial_benefit_new_ths(symbol, indicator='按年度')` — contains:
- `invest_income` — 投资收益 (dividends from subsidiaries, JV profit share)
- `fair_changes_income` — 公允价值变动收益 (mark-to-market gains on financial assets)
- `operating_profit` — already excludes these, so `operating_profit / operating_income` is the true operating margin

Note: `operating_profit` in Chinese accounting standards EXCLUDES investment income and fair value changes (they're below the line). So operating margin = `operating_profit / operating_income` is the cleanest single metric for core business profitability.
