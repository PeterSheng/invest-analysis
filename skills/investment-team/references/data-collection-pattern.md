# Data Collection Pattern: When web_extract Is Unavailable

## Problem

`web_extract` uses DuckDuckGo backend which only supports search, not content extraction. Browser tools may also be unavailable (missing system libraries on headless Linux). This leaves only `web_search` for data gathering.

## Solution: Multi-Round Targeted web_search

Use `execute_code` to run batches of `web_search` with progressively specific queries. Extract financial data directly from search result **snippets** (title + description), which often contain actual numbers from reputable financial sites.

### Round Structure: Progressive Refinement (Recommended)

The most effective pattern for investment-team analysis is **three progressive rounds**, each building on the last, all executed in parallel batches inside `execute_code`:

**Round 1 — Core Metrics (7-8 queries):** Stock price, market cap, latest quarter/annual financials, business segments, management, competitive position, valuation ratios, recent news. This round produces the headline numbers and shapes the analysis direction.

**Round 2 — Specific Deep Dive (5-7 queries):** Targeted at gaps from Round 1 — specific historical years, detailed segment breakdowns, dividend/buyback, AI/strategy, risk factors. Queries in this round are more specific because you now know what to ask.

**Round 3 — Precision Fill (4-6 queries):** Narrow queries for exact numbers that are still fuzzy — e.g., `"TICKER 2025 full year net revenues $ billion net earnings EPS diluted"` or `site:stockanalysis.com "Company" statistics ROE ROA`. This round also attempts to access SEC filings, annual reports, and stock analysis pages for the final precise figures.

> **Progressive principle:** Don't try to get everything in one round. Round 1 tells you what you don't know → Round 2 fills the big gaps → Round 3 gets the decimal points right.

Run all queries within each round in **parallel inside `execute_code`** (not sequential tool calls) to minimize latency.



### Best Sources (appear reliably in snippets)

| Source | What It Provides |
|--------|-----------------|
| **Stock Analysis** (`stockanalysis.com`) | TTM revenue, net income, market cap, PE ratio — the `/stocks/TICKER/` page returns key stats in search snippets |
| **SEC Filings** (`sec.gov`) | H1/H2 revenue, net earnings, segment-level data — earnings releases on sec.gov have structured tables |
| **Earnings coverage** (CoinAlertNews, Money Morning, Benzinga, MarketScreener) | Q-specific: revenue, EPS, YoY growth %, segment breakdown, ROE/ROTE |
| **Earnings presentations** (PDF on goldmansachs.com, etc.) | Slide-level data: record revenue, segment breakdown, BVPS, AUM/AUS |
| **Competitor comparison** (FourWeekMBA, PitchGrade) | Cross-company data: "Jane Street $10.3B → Goldman $31.1B trading revenue" |
| **Lightyear** (`lightyear.com`) | Stock price, market cap, dividend rate, yield, payout ratio |
| **SimplyWallSt** (`simplywall.st`) | Total assets, liabilities, EBIT, interest coverage, cash, PE vs peers |
| **Insurance Journal** / **MarketWatch** | Acquisition details, lawsuit details, employee counts |
| **GuruFocus** (`gurufocus.com`) | PE ratio history, specific valuation dates |
| **MarketChameleon** | Recent stock price with exact date, market cap |
| **FXStreet / Motley Fool** | Analyst commentary with embedded valuation metrics (Forward PE, PEG, PB) |

### Data Extraction from Snippets

Key technique: **search snippets contain the actual numbers**. Example:
- "As of June 30, 2026, BRO stock price declined to $63.65 with ... market cap of $21.57 billion"
- "2024 free cash flow was $1.09B, which is 109.7% of reported net income" → NI = 1.09/1.097 = $0.993B
- "Brown & Brown reported Q1 2026 revenue of $1.9 billion ... adjusted diluted EPS rose to $1.39 while GAAP diluted EPS was $1.06"
- "total assets and total liabilities are $15.9B and $9.9B respectively ... EBIT is $1.3B making its interest coverage ratio 11"

### Filling Gaps

When exact historical data is unavailable, use consistent estimation:
- **Net income from FCF ratio**: NI = FCF / (FCF/NI ratio)
- **PE from price and EPS range**: From "shares trade at 18.4x earnings" + "current price $63.65"
- **Annual revenue trends**: From YoY growth rates mentioned in earnings releases

### Pitfalls

| ❌ Don't | ✅ Do |
|---------|------|
| Search for year ranges like "2022 2023 2024" all at once | Search for "2024 annual" separately, then backfill prior years |
| Search in Chinese for US stocks | Always use English queries for US stock data |
| Try to scrape macrotrends.net directly | The snippets are sufficient — macrotrends blocks scraping |
| Use sequential `web_search` tool calls | Batch all queries in one `execute_code` call |
| Search for all financial data in one query | Split into phases: (1) price+mcap+PE, (2) annual financials, (3) quarters+segments, (4) events+management |
| Skip segment-level detail for diversified financials | Search separately for each business segment's revenue and growth — the total tells only half the story |
| Trust every data source at face value | Cross-validate: `advfn.com` sometimes returns garbage (e.g. P/E 0.08 for a $1T company). When a number looks absurd, search for it from another source before using it. |
| Run just one round and proceed to modeling | Progressive refinement: Round 1 identifies gaps → Round 2 fills them → Round 3 gets precision. Stopping after Round 1 leads to weak financial models. |
| **Assume `web_search` always returns `data.web` key** | **DuckDuckGo backend sometimes returns partial results or timeouts. Always guard with `.get('data', {}).get('web', [])` or try/except KeyError. When a batch query returns `KeyError: 'data'`, that specific query timed out — re-run it individually or skip it and backfill from other sources.** |
