# Ad/Platform Business Growth Sustainability Framework

> Applied in: Tencent advertising growth analysis (May 2026)
> Reusable for: any internet platform company's advertising/commercialization business

## Core Question

"How many more years can [Company]'s [advertising/monetization] business maintain above-market growth?"

## Analysis Framework (4 Steps)

### Step 1: Quantify the Loading Rate Gap

For any ad-supported platform, the single biggest growth driver is **ad load (广告加载率)** — the percentage of content impressions that carry ads.

| Metric | Source | Example (Tencent vs Douyin) |
|--------|--------|---------------------------|
| Target DAU | Company disclosures / earnings calls | 5亿 vs 7亿 |
| User time per day | Industry reports / analyst estimates | 60 min vs 120 min |
| Ad load % | Earnings call commentary / reverse-engineering | 3-4% vs 12-15% |
| Ad ARPU (annual) | Revenue / DAU | ~35元 vs ~120元 |

**Key insight:** Ad load gap × ARPU gap = total monetization gap. Even if ARPU stays lower, closing half the ad load gap alone can double or triple revenue.

### Step 2: Map Multi-Stage Growth Trajectory

Break future growth into clearly labeled stages with declining rates:

```
Stage 1 (Current → +2-3yr): Core driver, highest growth
  └─ Ad load normalization (3-4% → 6-8%)
  └─ CAGR: 15-20%

Stage 2 (+2-3yr → +4-6yr): Second engine kicks in
  └─ New monetization surfaces (search, e-commerce ads)
  └─ AI-driven eCPM improvements
  └─ CAGR: 10-14%

Stage 3 (+4-6yr → +8-10yr): Approaching ceiling
  └─ Ad load nearing industry norms
  └─ Growth converges to market average
  └─ CAGR: 5-8%

Stage 4 (10yr+): Steady-state cash cow
  └─ Follows GDP + digital ad market growth
  └─ CAGR: 3-5%
```

### Step 3: Calculate Market Share Ceiling

Two approaches:

**Top-down (market share):**
```
Target revenue = Total addressable market × realistic max share
Example: China digital ads 7,000亿 × 25-28% = 1,750-2,000亿
```

**Bottom-up (capacity):**
```
Target revenue = DAU × daily impressions × ad load × eCPM × 365
Example: 5亿 × 30 impressions × 8% × 0.05元 × 365 = 2,190亿
```

Cross-check both — they should roughly agree (±20%).

### Step 4: Identify Relay Engines (接力引擎)

Growth rarely comes from one source forever. Identify the baton-pass:

| Engine | When | Scale | Certainty |
|--------|------|-------|-----------|
| Primary (ad load) | Now → Y3 | Large | ⭐⭐⭐⭐⭐ |
| Secondary (new surface) | Y2 → Y5 | Medium | ⭐⭐⭐⭐ |
| Tertiary (AI/efficiency) | Now → forever | Small/steady | ⭐⭐⭐ |
| Quaternary (international) | Y5+ | TBD | ⭐⭐ |

## Competition Context

Always build a comparison table with the top 3-4 competitors:

| Dimension | Target | Competitor A | Competitor B |
|-----------|--------|-------------|-------------|
| Ad revenue (latest FY) | X | Y | Z |
| Market share | X% | Y% | Z% |
| Growth rate | X% | Y% | Z% |
| Ad load headroom | 3-4x | exhausted | limited |
| User moat | describe | describe | describe |

## AI 护城河型广告平台的领先指标（2026-08 AppLovin 实战）

For AI-engine-driven ad platforms (AXON/AppLovin, Meta ads), the growth narrative rests on **model improvement cadence**. Two leading indicators that beat quarterly revenue prints:

1. **模型改进节奏（model improvement cadence）**：当公司自认"AI 模型改进速度低于预期"（AppLovin Q2'26 miss 归因）——这是飞轮叙事**首次官方裂痕**，比营收 miss 本身更重要。跟踪信号：每季 eCPM / 每安装净收入提升幅度是否逐季递减。任何 AI 广告平台季度 miss，先查归因是否为模型改进放缓。

2. **增量率质疑（incrementality challenge）**：做空 ad-tech 的标准攻击面——指控高比例转化来自重定向（retargeting），增量率（incrementality，即"没有这个广告转化是否仍会发生"）远低于宣称。AppLovin：Muddy Waters 指控 52% 电商转化来自重定向、增量率仅 25-35% vs CEO 宣称 ~90%。增量率是反事实推断，**难以自证也难证伪**——做空者用模糊性制造怀疑，公司用内部数据否认。第三方增量率审计是唯一证伪/证实节点。

**处理纪律**：① 报告必须呈现指控方数字 vs 公司数字的对照表，不做单方采信；② 现价已跌 50%+ 时，问"市场定价的是哪个情景"——悲观 DCF 是否已覆盖罚款+数据受限+增速降至 18-20%；③ 平台数据依赖（租来的数据飞轮）使护城河评级打对折——SEC 调查"是否违反平台服务协议"直接攻击此点。

## Pitfalls

- **Don't assume linear ad load increases.** Platforms face user experience trade-offs. Tencent's WeChat team has a history of conservative monetization.
- **Macro sensitivity.** Advertising is cyclical — model a "recession case" where growth drops to 0-3% for 1-2 years.
- **Regulatory risk.** China's data privacy laws and antitrust enforcement can cap ad targeting capabilities.
- **Competitive response.** When you gain share, competitors don't sit still. Douyin will fight to retain advertiser budgets.
- **Ad load ≠ revenue linearly.** As you add more ad slots, eCPM typically declines (supply/demand). Model diminishing returns.

## Delivery Format

When answering "how many years of growth remain," the most impactful format is a **visual timeline table**:

```
Phase | Duration | CAGR | Key Driver | Confidence
🟢 High-growth | 2-3 yr | 15-18% | Ad load normalization | High
🟡 Mid-growth  | 2-3 yr | 10-14% | New surfaces + AI | Medium
🟠 Slowing     | 2-3 yr | 5-8%  | Market convergence | Medium
🔴 Steady-state| Beyond  | 3-5%  | GDP + market growth | Low
```

One-line answer template:
> "高确定性高增长（X%）还能维持 2-3 年，中速增长还能再续 2-3 年，之后增速逐步回落到与整体市场同步。'跑赢大盘'的窗口期大约还有 5-6 年。"
