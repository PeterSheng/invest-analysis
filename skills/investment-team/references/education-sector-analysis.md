# Education Company Analysis Framework

> Patterns and pitfalls specific to Chinese-listed education companies (教培行业).
> Companion to the main equity-investment-research skill.

## 1. The Deferred Revenue Trap (预收学费与真实负债率)

Education companies collect tuition upfront but recognize revenue over the service period. This means:

- **Reported debt ratio (70-80%) is MISLEADING.** Most "liabilities" are contract liabilities (预收学费), not interest-bearing debt.
- To assess true leverage, check balance sheet for `BORROW_FUND`, `SHORT_LOAN`, `LONG_LOAN` — if these are `null`/`None`, the company likely has zero bank debt.
- **Estimated real leverage:** Total liabilities minus ~60-70% (deferred revenue portion) ≈ 25-35% real debt ratio.
- **However:** prepaid tuition is still a liability — if the company collapses, it must refund. It's just not interest-bearing.

## 2. The OCF/NP Premium (经营现金流远高于净利润)

```
Typical education company: OCF/NP = 3-4x
Normal manufacturer:     OCF/NP ≈ 1.0-1.5x
```

Why: prepaid tuition model means cash arrives months before revenue recognition. This creates:
- Very strong operating cash flow (7.39亿 OCF vs 1.95亿 NP for 学大教育 FY2025)
- BUT: OCF premium shrinks when growth slows (less incremental deferred revenue)

**For DCF:** Don't use the raw OCF as FCF — the premium reflects growth, not sustainable cash generation.
Use FCF = NP × 1.5-2.0x as a conservative steady-state estimate (vs 3.8x observed).

## 3. Seasonality Patterns (强季节性)

| Quarter | Revenue Pattern | OCF Pattern | Reason |
|---------|:---:|:---:|------|
| Q1 | Weakest (~25% of annual) | **Strongest** (spring enrollment) | Winter break short, but spring semester prepaid |
| Q2 | Moderate (~22%) | Weak | Mid-semester, few new enrollments |
| Q3 | **Strongest** (~30%) | Strong | Summer vacation = peak tutoring season |
| Q4 | Moderate (~23%) | Moderate | Fall semester |

Always use TTM (trailing 12-month) for PE calculation, never single-quarter annualized.

## 4. Regulatory Risk Framework (双减教训)

The 2021 "双减" (Double Reduction) policy is the defining event for this sector:

| Metric | Pre-双减 (FY2021H1) | Post-双减 (FY2021 full year) | Impact |
|--------|:---:|:---:|:---:|
| 学大教育 Revenue | ~15.8亿 (H1) | 25.3亿 → 17.98亿 (-29%) | Massive |
| 学大教育 Net Profit | +1.1亿 (H1) | **-5.36亿** | Catastrophic |
| 学大教育 Net Assets | ~10.7亿 | 4.3亿 (-60%) | Near-fatal |
| Stock Price | ~70元 | ~10元 (-86%) | Wealth destruction |

**Key lessons for analysis:**

1. **Regulation is existential risk.** No DCF survives a regulatory shutdown. Always include a "regulatory tail risk" section.
2. **Current "one-on-one" tutoring is a grey zone.** It wasn't explicitly banned in 双减 (which targeted K9 subject-based tutoring), but could be in future waves.
3. **Check what's actually happening:** Look for recent government signals — new licenses being issued (positive) vs enforcement actions (negative).
4. **Diversification matters.** Companies that pivoted to vocational education, adult learning, or non-academic training have lower regulatory exposure.

## 5. AI Disruption Risk (AI家教)

This is a NEW threat (wasn't present during 双减):

- AI tutors (豆包爱学, 猿辅导AI, ChatGPT) can provide personalized tutoring at near-zero marginal cost
- Most threatening to **mid-to-low-end one-on-one tutoring** — precisely 学大教育's core market
- High-end tutoring (exam-specific strategies, motivation coaching) is more defensible
- This is a "technology disruption" risk — Buffett's #1 reason to avoid an industry

## 6. What Buffett Would Look For

Education companies that pass a Buffett screen would need:
- ✅ Zero regulatory ambiguity (adult vocational training, not K12 tutoring)
- ✅ Recurring revenue with high retention rates
- ✅ Brand that parents genuinely trust (hard to build post-双减)
- ✅ Asset-light, high-margin (>20% net margin)
- ❌ Chinese K12 tutoring fails most of these tests

**Bottom line:** Most Chinese education stocks fall into Buffett's "Too Hard" pile due to regulatory uncertainty. They are at best "cigar butt" or special situation investments, not compounders.
