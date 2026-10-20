# Valuation Approach Selection Matrix

> How to pick the right valuation method for different company profiles in Buffett-style analysis.
> Battle-tested on Backblaze (unprofitable growth), VTech (no-growth dividend), Pop Mart (hyper-growth) — Jun 2026.

## Company Profile → Primary Valuation Method

| Company Profile | Primary Method | Secondary Method | Skip |
|:---|:---|:---|:---|
| **Stable profitable, predictable** | DCF (10yr, moderate growth) | PE multiples vs peers | — |
| **No-growth / declining (value trap risk)** | DDM or Owner Earnings yield | DCF with 0% terminal growth, liquidation floor | High-growth DCF |
| **Unprofitable but approaching breakeven** | Revenue multiples (EV/Rev vs peers) | DCF with SBC adjustment, acquisition comp | Simple PE |
| **Hyper-growth (>50% YoY)** | DCF with aggressive growth deceleration | Peer PE multiples (global peers), PEG | Current PE as primary |
| **Cyclical / commodity** | Normalized PE (10yr avg earnings) | Mid-cycle DCF, P/B | TTM PE |
| **Asset-heavy / insurance** | P/B + BVPS growth | — | DCF |
| **High SBC / dilution** | Always compute **economic FCF = FCF - SBC** | Revenue multiples as sanity check | Ignoring SBC |

## Key Rules

### 1. Always compute Economic FCF (FCF minus SBC)
For any company with material stock-based compensation (>5% of revenue), economic FCF is the true shareholder return. Example: Backblaze FY2025 FCF = +$18.8M but SBC = $26.4M → Economic FCF = -$7.6M. The accounting FCF is deceptive.

### 2. When DCF and revenue multiples diverge by >50%, trust the method that fits the profile
For unprofitable growth companies, DCF often gives absurdly low values because near-term losses dominate the PV. Revenue multiples (benchmarked to profitable peers) are often more informative. Quote both but explain the divergence.

### 3. For no-growth / declining companies, zero terminal growth is mandatory
Do NOT apply 3% terminal growth to a company with 9 years of zero revenue growth (e.g., VTech). The DCF value from terminal growth alone can be >100% of the total — this is a sign your terminal assumption is wrong. Use 0% or even -1% for declining industries.

### 4. Hyper-growth companies need aggressive deceleration curves
When a company grows 185% in one year (Pop Mart), project revenue deceleration over 5-10 years: 50%→35%→25%→20%→15%... Never project >30% growth beyond year 5 without extraordinary justification. The market rarely prices >30% sustained growth correctly — that's where value traps form.

### 5. Dividend sustainability check is mandatory for high-yield stocks
If dividend yield >5%, compute:
- Payout ratio (DPS/EPS)
- OCF coverage (DPS/OCF_per_share)
- Sustainable DPS at 80% payout

If payout >100% or OCF coverage <100%, flag the dividend as unsustainable and compute the "reset" share price at sustainable yield.

### 6. Peer selection must match business mix
For conglomerates/hybrids, identify the revenue mix and select peers for each segment. Weighted-average peer PE is more accurate than picking one peer. Example: VTech = 40% ELP (toy peer PE) + 35% TEL (declining hardware PE) + 25% CMS (EMS peer PE).

## Scenario Weighting Defaults

| Risk Profile | Bear | Base | Bull |
|:---|:---:|:---:|:---:|
| Mature / predictable | 20% | 60% | 20% |
| Growth with uncertainty | 25% | 55% | 20% |
| Turnaround / unprofitable | 35% | 45% | 20% |
| Hyper-growth / unproven | 20% | 55% | 25% |
| Declining industry | 30% | 50% | 20% |
