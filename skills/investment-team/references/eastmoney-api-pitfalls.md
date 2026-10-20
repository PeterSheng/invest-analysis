# EastMoney API — Data Reliability & Pitfalls

> Companion to `tencent-finance-api-format.md`. Documents which EastMoney API endpoints and fields work correctly and which return garbage data.
> 
> **For the complete end-to-end research workflow, see `research-data-pipeline.md`** — covers optimal API call sequence, parallel fire pattern, and how to assemble a full Buffett analysis when web search is unavailable.

## 1. Reliable Endpoints & Fields

### RPT_F10_FINANCE_MAINFINADATA (核心财务数据) — ✅ Generally Reliable

**URL pattern:**
```
https://datacenter.eastmoney.com/securities/api/data/v1/get?
  reportName=RPT_F10_FINANCE_MAINFINADATA
  &columns=SECURITY_CODE,REPORT_DATE,TOTALOPERATEREVE,PARENTNETPROFIT,EPSJB,BPS,XSJLL,ROEJQ,ZCFZL,TOTAL_SHARE
  &filter=(SECURITY_CODE="688029")
  &sortColumns=REPORT_DATE&sortTypes=-1&pageNumber=1&pageSize=12
```

**Trusted fields (✅ = verified reliable):**

| Field | Meaning | Trust |
|:---|:---|:---:|
| TOTALOPERATEREVE | 营业总收入 | ✅ |
| PARENTNETPROFIT | 归母净利润 | ✅ |
| EPSJB | 基本每股收益 | ✅ |
| BPS | 每股净资产 | ✅ |
| XSJLL | 销售净利率(%) | ✅ |
| ROEJQ | 净资产收益率(%) | ✅ (加权后) |
| ZCFZL | 资产负债率(%) | ✅ |
| TOTAL_SHARE | 总股本 | ✅ |

**UNRELIABLE fields (❌ = returns garbage/zero):**

| Field | Meaning | What it actually returns | Workaround |
|:---|:---|:---|:---|
| MLR | 毛利率(%) | Raw values like 546471756.9 (gross profit in 元?) | Compute manually from income statement or check annual report |
| JYXJLYYSR | 经营活动现金流 | Always 0.00 for all periods | Get from annual report directly |
| RDEXPEND | 研发费用 | 0.00 for quarterly reports, works only for annual | Filter by REPORT_DATE ending in -12-31 |

### RPT_F10_FINANCE_INCOME (利润表) — ⚠️ Unreliable

- Often returns `null` or empty arrays for certain stocks (tested: 688029 南微医学 returned empty)
- When it does return data, URL encoding of Chinese characters in filter params causes `UnicodeEncodeError`
- **Recommendation:** Skip this endpoint. Use MAINFINADATA for bottom-line numbers.

### RPT_DMSK_FN_INCOME (利润表, alternate endpoint) — ⚠️ Field names differ from MAINFINADATA

- This endpoint uses DIFFERENT field names from `RPT_F10_FINANCE_MAINFINADATA`
- `BASIC_EPS` → **REJECTED** ("BASIC_EPS返回字段不存在")
- `TOTAL_OPERATE_INCOME`, `PARENTNETPROFIT`, `WEIGHTAVG_ROE` → work correctly
- `GROSS_PROFIT_RATIO` → may work but verify
- `SALE_GROSS_PROFIT_RATIO` → may also work (test per stock)
- **Recommendation:** Use `RPT_F10_FINANCE_MAINFINADATA` (with `EPSJB`, `XSJLL`, `ZCFZL` etc.) as primary. If you must use `RPT_DMSK_FN_INCOME`, test field names individually. `TOTAL_OPERATE_COST` works for cost data — compute gross margin manually: `(TOTAL_OPERATE_INCOME - TOTAL_OPERATE_COST) / TOTAL_OPERATE_INCOME`.

### RPT_F10_FINANCE_ANALYSIS (财务分析指标) — ❌ Does Not Exist

- Returns "报表配置不存在,RPT_F10_FINANCE_ANALYSIS"
- Do not use

### RPT_F10_ORG_INCOMESTRU (主营构成) — ⚠️ Intermittent

- Sometimes returns product segment breakdown with gross margins
- Fields: PRODUCT_NAME{i}, PRODUCT_INCOME{i}, PRODUCT_RATIO{i}, PRODUCT_GPR{i}
- Tested May 2026: returned null for 688029
- **Recommendation:** Try it but always have a fallback plan

## 2. Stock Quote — Tencent API (gtimg.cn)

**Always use as primary/verification source.** See `tencent-finance-api-format.md` for full field mapping.

```
https://qt.gtimg.cn/q=sh688029
https://qt.gtimg.cn/q=hk00700
https://qt.gtimg.cn/q=usFUTU
```

Key fields for A-shares:
- `fields[3]` = 现价
- `fields[39]` = PE(TTM)
- `fields[44]` = 市值(亿)
- `fields[45]` = 总股本(亿)
- `fields[4]` = 昨收

## 3. Cross-Verification Protocol

For any analysis, verify these data points across at least 2 sources:

| Data Point | Primary Source | Verification Source |
|:---|:---|:---|
| Stock Price | Tencent qt.gtimg.cn | EastMoney MAINFINADATA (EPS × PE implied) |
| Market Cap | Tencent (field[44] × 1e8) | price × total_shares |
| Net Profit | EastMoney PARENTNETPROFIT | If HK stock: AKShare stock_financial_hk_analysis_indicator_em |
| Gross Margin | Annual report (manual) | Compute: (revenue - cost)/revenue if cost data available |
| OCF | Annual report (manual) | Do not trust EastMoney JYXJLYYSR field |

## 4. URL Encoding Gotcha

When using EastMoney API with Chinese characters in filters:
```python
# WRONG — causes UnicodeEncodeError
url = f"...&filter=(REPORT_TYPE="年报")"

# RIGHT — use urllib.parse.quote
params = urllib.parse.urlencode({...}, quote_via=urllib.parse.quote)

# Or avoid Chinese filters entirely — use REPORT_DATE pattern matching instead
```

## 5. Balance Sheet & Cash Flow APIs

### RPT_DMSK_FN_BALANCE (资产负债表) — ✅ Works but field names vary by stock type

- Column names are **not the same** as the common field labels (e.g., `CONTRACT_LIAB` doesn't exist; use `ADVANCE_RECEIVABLES` for 预收款)
- **Field discovery trick:** Query with `columns=ALL` first to see which fields actually exist for the stock:
  ```
  &columns=ALL&filter=(SECURITY_CODE="000526")&pageSize=1
  ```
  Then inspect the returned JSON keys to find real field names.
- Reliable fields discovered so far:
  - `TOTAL_ASSETS`, `TOTAL_LIABILITIES`, `TOTAL_EQUITY`
  - `MONETARYFUNDS` (货币资金), `ACCOUNTS_RECEIVABLE` (应收账款) — confirmed Jul 2026 for 600809. Note: `ACCOUNTS_RECE` also works for some stocks, but `ACCOUNTS_RECEIVABLE` appears more reliable.
  - `ADVANCE_RECEIVABLES` (预付款项) — NOT contract liabilities
  - `ACCOUNTS_PAYABLE` (应付账款)
  - `DEBT_ASSET_RATIO` (资产负债率%)
  - `BORROW_FUND` — `null` if no bank borrowings (good sign)
  - `SHORT_LOAN`, `LONG_LOAN` — may be `null` for companies with no bank debt
- ⚠️ `CONTRACT_LIAB` (合同负债/预收学费) is NOT available in this endpoint. For education/ service companies, estimate from OCF patterns.
- ⚠️ `QUICK_RATIO` — confirmed REJECTED for 600809 ("QUICK_RATIO返回字段不存在"). Use `CURRENT_RATIO` only or compute manually.
- ⚠️ `EQUITY_RATIO` — may return `null` for some stocks, use `DEBT_ASSET_RATIO` + compute inverse if needed.

### RPT_DMSK_FN_CASHFLOW (现金流量表) — ✅ Reliable

```
&columns=SECURITY_CODE,REPORT_DATE,NETCASH_OPERATE,NETCASH_INVEST,NETCASH_FINANCE,SALES_SERVICES
```

- `NETCASH_OPERATE` — 经营活动现金流净额 ✅
- `NETCASH_INVEST` — 投资活动现金流 ✅ (includes both maintenance and growth capex)
- `NETCASH_FINANCE` — 筹资活动现金流 ✅
- `SALES_SERVICES` — 销售商品提供劳务收到的现金 ✅ (useful for OCF/Revenue ratio)
- ⚠️ `NETCASH_OPERATE_YOY` — **REJECTED** ("NETCASH_OPERATE_YOY返回字段不存在"). Compute YoY manually from `NETCASH_OPERATE` values.
- OCF/Revenue ratio > 40% in Q1 is normal for education companies (spring semester enrollment)
- For FCF estimation: OCF - maintenance capex ≈ OCF - ~40% of NETCASH_INVEST (rest is growth capex)

## 6. Qualitative Data — Working PC_HSF10 Endpoints

When browser tools are unavailable (e.g., missing Chrome libraries), these EastMoney PC_HSF10 endpoints provide rich qualitative data via `curl`. They are more reliable than the datacenter `RPT_*` endpoints for business analysis.

### PC_HSF10/CompanySurvey/CompanySurveyAjax — Company Profile ✅

```
https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/CompanySurveyAjax?code=SZ002884
```

Returns JSON with `jbzl` (基本资料) containing:
- `gsmc` — company full name (公司全称)
- `gsjj` — **rich company description** (公司简介, includes history, products, certifications, capacity)
- `jyfw` — business scope (经营范围)
- `zjl` / `frdb` / `dsz` — CEO / legal rep / chairman
- `gyrs` — employee count (员工人数)
- `sshy` / `sszjhhy` — industry classification
- `gswz` — company website
- `zczb` — registered capital

Also returns `fxxg` (发行相关) with IPO date, listing date, IPO PE ratio, IPO price.

### PC_HSF10/CoreConception/PageAjax — Business & Moat Analysis ✅✅✅ (MOST VALUABLE)

```
https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/PageAjax?code=SZ002884
```

Returns JSON with `hxtc` (核心题材) array. Each entry has:
- `KEYWORD` — topic: 经营范围, 主营业务, 行业背景, 核心竞争力
- `MAINPOINT_CONTENT` — **detailed narrative text** for that topic
- `IS_POINT` — "1" = key point

This is the BEST single source for:
- **Business model** (主营业务) — full product list with applications
- **Industry data** (行业背景) — includes market size, growth rates, industry trends from trade associations
- **Moat analysis** (核心竞争力) — company's own articulation of competitive advantages (技术研发, 品牌, 规模, 客户资源)

Use `grep` or `python3 -c` to extract specific MAINPOINT_CONTENT fields.

⚠️ **Python f-string nested bracket gotcha:** When extracting from JSON with list comprehensions, nested brackets inside f-strings cause `SyntaxError: f-string: unmatched '['`. **Do NOT do this:**
```python
# BROKEN — nested [ inside f-string expression
[print(f"{t['KEYWORD']}", t['MAINPOINT_CONTENT'][:3000]) for t in d['hxtc']]
```
**Use string concatenation instead:**
```python
# CORRECT — no nested brackets inside f-string
for t in d.get('hxtc', []):
    print('=== ' + t.get('KEYWORD','') + ' ===')
    print(t.get('MAINPOINT_CONTENT','')[:3000])
```

Also returns `ssbk` (所属板块) for sector/theme classification.

### PC_HSF10/OperationsRequired/PageAjax — Combined Financial + News Feed ✅

```bash
https://emweb.securities.eastmoney.com/PC_HSF10/OperationsRequired/PageAjax?code=SZ002223
```

Returns a multi-section JSON with:
- `zxzb` — latest quarter financial indicators (EPS, BPS, revenue, ROE, debt ratio, gross margin, revenue/profit growth rates). Note: `zxzb` is an **array** (wrapped in `[]`), not an object. Access: `data["zxzb"][0]["EPSJB"]`.
- `zxzbOther` — PE(动态/静态/TTM), PB, total market cap. Same array wrap: `data["zxzbOther"][0]["TOTAL_MARKET_CAP"]`.
- `zxzbhq` — **flat-key version of zxzbOther** (easier to parse). Uses numeric keys: `f116`=总市值, `f117`=流通市值, `f162`=PE动态, `f163`=PE静态, `f164`=PETTM, `f167`=PB. No array wrapper — access directly with `data["zxzbhq"]["f116"]`.
- `zxzx` — latest 5 news articles with titles and summaries
- `zxgg` — latest announcements (分红, 季报等)
- `dstx` — corporate event timeline (分红送转, 报表披露, 投资互动)

Financial fields include gross margin (`XSMLL`), revenue YoY growth (`TOTALOPERATEREVTZ`), net profit YoY growth (`PARENTNETPROFITTZ`), and per-share metrics.

Note: Some fields have `_LAST` suffix variants (e.g., `TOTAL_OPERATEINCOME_LAST`) which contain the prior-year-same-quarter value for YoY comparison.

### PC_HSF10/Management/PageAjax — ❌ Returns "无F10资料"

- Tested June 2026: returns HTML page saying "无F10资料" for 002884
- Do not use

### PC_HSF10/BusinessAnalysis/PageIndex — ❌ Returns "无F10资料"

- Tested June 2026: returns HTML page saying "无F10资料" for 002884
- Do not use

## 8. Stock Discovery — Smartbox API

When the user gives a company name that doesn't match any known ticker (or uses the full legal name instead of the stock abbreviation), use Tencent's smartbox to find the stock code:

```
https://smartbox.gtimg.cn/s3/?q=鼎熔岩&t=all
```

Returns: `v_hint="sz~301028~\u9f0e\u7194\u5ca9~dry~GP-A"` — the stock code is in the second `~`-delimited field.

Also works with partial names, pinyin, and English names. Always verify the returned name matches the user's intent.

## 9. AKShare Endpoint Reliability Matrix

AKShare is installed and is the preferred Python library for financial data. However, not all endpoints are equally reliable in production. This section documents which ones survive network turbulence and which ones fail.

### ✅ HIGH RELIABILITY — use these as primary data sources

| Endpoint | What It Returns | Reliability |
|:---|:---|:---|
| `stock_financial_abstract_ths(symbol, indicator='按年度')` | Income statement summary (营收,净利,毛利率,ROE等) | ✅✅✅ — most resilient, works when spot/hist fail |
| `stock_financial_abstract(symbol)` | Extremely wide DataFrame — ALL financial indicators as rows, ALL reporting periods as columns (back to 1990) | ✅✅ — works when THS endpoints fail. Key indicators match by partial string (`'营业总收入' in str(row['指标'])`). Filter columns ending in '1231' for annual data |
| `stock_financial_analysis_indicator(symbol, start_year='20XX')` | Detailed financial ratios (all DuPont components, turnover ratios, per-share metrics) | ✅✅✅ — very reliable, comprehensive. ⚠️ Can return empty DataFrame for some stocks (e.g., 600809 山西汾酒 returned empty in July 2026); fall back to `stock_financial_abstract` |
| `stock_financial_benefit_new_ths(symbol, indicator='按年度')` | Detailed P&L (pivotable by metric_name) | ✅✅ — works, needs pivot logic |
| `stock_financial_cash_new_ths(symbol, indicator='按年度')` | Cash flow statement | ✅✅ — works, cross-reference with net profit |
| `stock_financial_debt_new_ths(symbol, indicator='按报告期')` | Balance sheet (filter to -12-31) | ✅✅ — works |

### ❌ LOW RELIABILITY — frequently fail with connection errors

| Endpoint | Failure Mode | Fallback |
|:---|:---|:---|
| `stock_individual_info_em(symbol)` | `RemoteDisconnected` — remote end closed connection | Use Tencent API for price/valuation |
| `stock_zh_a_spot_em()` | Same connection error, especially when fetching the full market (too much data) | Use Tencent API |
| `stock_zh_a_hist(symbol, ...)` | Same connection error | Use `stock_financial_abstract_ths` for earnings history |

### Pattern: When EastMoney real-time endpoints are down

The EastMoney `push2` websocket-based endpoints (`stock_individual_info_em`, `stock_zh_a_spot_em`, `stock_zh_a_hist`) frequently fail in server environments. The more reliable endpoints are the THS (同花顺) abstract endpoints in AKShare and the Tencent HTTP API.

**Resilient data pipeline when real-time APIs fail:**
1. **Price/Valuation** → Tencent `qt.gtimg.cn` (always works, no auth needed)
2. **Financial history** → AKShare `stock_financial_abstract_ths` + `stock_financial_analysis_indicator`
3. **Qualitative data** → If PC_HSF10 works: CoreConception/CompanySurvey. If not: domain knowledge with ⚠️ flags

## 10. Degraded Mode — When Everything Is Down

In some server environments:
- Google, Bing unreachable (Network is unreachable)
- DuckDuckGo returns no useful snippets
- Browser tools may fail due to missing Chrome dependencies (`libatk-1.0.so.0: cannot open shared object file`)
- EastMoney `datacenter` API may return empty responses
- EastMoney `PC_HSF10` endpoints may be intermittently unreachable
- Subagent (`delegate_task`) web search times out after 600s with no useful output (46+ API calls, all failing)
- `python3 -c "import requests..."` may fail with `Connection aborted` errors — use `curl` instead

**Nuclear fallback — what ALWAYS works:**
1. `curl -s "http://qt.gtimg.cn/q=szCODE" | iconv -f gbk -t utf-8` — stock quote (price, PE, PB, market cap)
2. AKShare `stock_financial_abstract_ths` + `stock_financial_analysis_indicator` — financial history
3. Domain knowledge for competitive landscape, industry outlook, moat analysis

**When relying on domain knowledge:** Flag estimated/recalled data with ⚠️ in the report. Cross-verify financial numbers (which come from API) against desktop knowledge (which is approximate). Never fabricate API data — if an endpoint fails, mark that section as "data unavailable due to API restrictions" rather than guessing numbers.
