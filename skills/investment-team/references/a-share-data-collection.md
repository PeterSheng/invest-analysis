# A-Share Data Collection Reference

> Supplement to `data-collection-pattern.md` — specific to Chinese A-share stocks (沪深A股).

## Reliable Chinese Data Sources

| Source | URL Pattern | What It Provides |
|--------|------------|-----------------|
| **看财报 (kancaibao.com)** | `/jidu/tonbi/{code}/4` | Exact annual revenue, net income in 元 — most reliable for historical data |
| **证券之星** | search snippets | Annual report summaries with revenue, NI, YoY growth |
| **格隆汇** | search snippets | Earnings releases with exact financials and dividends |
| **雪球 (xueqiu.com)** | `/S/SH{code}` or `/S/SZ{code}` | User discussions often contain extracted data tables |
| **同花顺 (10jqka.com)** | `/stockpage/{code}/` | PE, PB, market cap, real-time quotes |
| **亿牛网 (eniu.com)** | `/gu/sh{code}` | Historical PE, PB, ROE, BVPS, dividend data |
| **东方财富 (eastmoney.com)** | search snippets | Market data, research reports |
| **新浪财经** | search snippets | Stock quotes, financial data |
| **英为财情 (Investing.com)** | search snippets | Current market cap, PE, employee count |
| **联合资信 (lhratings.com)** | PDF reports | Credit rating reports with detailed balance sheet |
| **Simply Wall St** | English queries | Market cap, PE for cross-validation |

## Key Differences from US Stocks

1. **No SEC filings** — annual reports are on cninfo.com.cn or company websites, harder to scrape
2. **Units are 元/亿元** — 万=10K, 亿=100M. Be careful: 109.41亿 = 10,941,000,000
3. **Market cap units** — Chinese sites use 亿, English sites use B. 1400亿 = 140B CNY ≈ $19B USD
4. **Share count** — reported as 亿股 (e.g., 13.4亿股 = 1,340M shares)
5. **EPS** — reported as 元/股, not adjusted for ADR ratios
6. **PE calculation** — sometimes uses TTM, sometimes trailing year; cross-validate

## akshare 实测：东财接口失败时的同花顺兜底（2026-08 拓荆科技 688072 实战）

- ❌ `ak.stock_financial_analysis_indicator_em(symbol="688072")` 报错 `'NoneType' object is not subscriptable`（东财接口不稳定/字段变更）
- ✅ 兜底：`ak.stock_financial_abstract_ths(symbol="688072", indicator="按报告期")` — 一次返回全历史报告期，字段含：净利润/扣非净利润/营业总收入/基本每股收益/每股净资产/每股经营现金流/销售净利率/销售毛利率/净资产收益率/资产负债率，足够跑完整 A 股 DuPont+DCF 模型
- 筛选年报：`df[df['报告期'].astype(str).str.contains('12-31')]`
- ⚠️ `ak.stock_financial_analysis_indicator_ths` 不存在（无此属性），正确名称是 `stock_financial_abstract_ths`
- 东财失败重试一次仍失败就直接切同花顺，不要反复重试浪费轮次

## 腾讯行情 API：A股 sh/sz 前缀（2026-08 拓荆科技实测）

`https://qt.gtimg.cn/q=sh688072`（A股用 sh/sz 前缀，港股 hk，美股 us）

已验证字段（⚠️ 与港股/美股索引不同，勿照搬 hk-stock-data-sources.md 的索引表）：

| 索引 | 含义 | 示例（拓荆 2026-08-07） |
|:---:|------|------|
| 3 | 最新价 | 690.65 |
| 31 / 32 | 涨跌额 / 涨跌幅% | 8.62 / 1.26 |
| 33 / 34 | 当日高 / 低 | 702.91 / 670.00 |
| 39 | PE(TTM) | 122.10（验证：市值÷PE ≈ 独立算出的 TTM 净利 ✓）|
| 45 | 总市值（亿RMB） | 2007.57（验证：价格×[73]总股本 ✓）|
| 72 / 73 | 流通股本 / 总股本（股） | 282693012 / 290678984 |

⚠️ 仅 [3][39][45][72][73] 双重验证过；PB、52周高低等其余字段索引未验证，需交叉核对。

### 腾讯日K接口（akshare 东财日线断连时的兜底，2026-09 星宇股份 601799 实战）

`ak.stock_zh_a_hist` 连续 3 次 `RemoteDisconnected`（东财接口不稳定）时，改用腾讯日K接口一次成功：

```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh601799,day,,,400,qfq
# 参数: {前缀}{代码},day,起始,结束,条数,qfq(前复权) — 400 条覆盖 ~1.5 年
```

- 返回 JSON：`data.sh601799.qfqday`（或 `day`）= 二维数组，每行 **7 个元素**（date/open/close/high/low/volume/未知字段）——直接 `pd.DataFrame(days, columns=[6个])` 会报 `6 columns passed, passed data had 7 columns`。**必须先 `rows = [d[:6] for d in days]` 截断到前 6 列**
- 52周高低/YTD/年末收盘直接算；字段均为字符串需 astype(float)
- 该接口 2026-09-02 实测：日线正常、JSON 解析稳定，作为 akshare 东财源断连时的首选兜底

### ⚠️ 腾讯 A 股字段实测补充（2026-09 华东医药 000963）
- **[47] PB 字段不可信**（华东医药显示 30.12，实际 27.35/14.51 = 1.89——垃圾值）；**[48]/[49] 是涨停/跌停价**（24.64/2.15），不是 52 周高低
- **52 周高低用 `ak.stock_zh_a_hist` 日线算**：`df[df['日期'] >= 今天-365天]` 取 max/min + 日期（华东医药：25.63@2026-06-29 / 46.15@2025-09-03 ✓）；该接口偶发 `RemoteDisconnected` 瞬时断连——for 循环重试 2-3 次即可
- **PE(TTM) 验证链**：`市值 ÷ (年报净利 − 上年H1净利 + 今年H1净利)`（华东：479.65/(34.14-18.15+18.61) = 13.86 ✓ 与 [39] 吻合）；同花顺摘要给 2026-06-30 行即中报已披露，H1 数据直接从表取
- **东财报表接口 REPORT_DATE 是 Timestamp**，to_num() 会把它变成 None（打印显示陷阱，数据没丢）；**报告期反推法：TOTAL_PARENT_EQUITY ÷ BVPS ≈ 总股本即锁定报告期**（华东 2026H1：254.4 亿 ÷ 14.51 = 17.54 亿股 ✓，与 [73] 总股本吻合——无需依赖日期列）
- **全年股息率必须含中期分红**：`ak.stock_fhps_detail_em` 一条命令拿全分红历史（含中期 10 派 X 的独立记录）；全年 DPS = 年报派息 + 中期派息（华东 2025：0.58+0.35 = 0.93 元 → 股息率 3.4%、分红率 48%）。只看年报派息会低估股息率约 40%

### ⚠️ A+H 两地上市 A 股（海康威视 002415 等）
- 腾讯 A 股行情市值字段可能只含 A 股口径；总股本验证配方：**公司公告分红总额 ÷ 每股分红**（海康 2026 中期分红 50.41 亿 ÷ 0.55 元 = 91.65 亿股 ✓ 与腾讯总股本字段吻合）
- 摊薄 EPS 与加权 EPS 差异大 = 年内股本变动（回购注销），勿用单一口径反推股本（海康 2025：摊薄 1.684 vs 加权 1.546）

### ⚠️ 东财现金流接口排序陷阱（海康实战）
- `stock_cash_flow_sheet_by_report_em` 返回的报告期**不按时间排序**，直接 tail() 取到最早年份（tail(5) 拿到 2006-2010 数据）
- 正确：`df['REPORT_DATE'].astype(str)` 后 `sort_values('REPORT_DATE')` 再筛选

### ⚠️ 同花顺摘要报告期**升序**陷阱（正泰电器 2026-08 实战）
- `ak.stock_financial_abstract_ths(symbol="601877", indicator="按报告期")` 返回**按报告期升序**（2006 在 index 0），`head(8)` 拿到的是 2006-2013 年数据！
- 正确：`df[df['报告期'].astype(str).str.contains('12-31')].tail(7)` 取最新年报；中报筛选 `06-30` 同样用 tail
- 已验证字段全集（够跑完整 A 股 DuPont+DCF）：净利润/扣非净利润/营业总收入/基本每股收益/每股净资产/每股经营现金流/销售净利率/销售毛利率/净资产收益率/资产负债率
- 东财资产负债表 `stock_balance_sheet_by_report_em` 同样是 `sort_values('REPORT_DATE')` 后 tail——**所有东财 report 类接口统一先 sort 再取尾部**

### 中报分项数据抓取：p5w.net 全景网
- 8 月分析 A 股先检查中报是否已披露：新浪 `stock_financial_analysis_indicator` 出现 `2026-06-30` 行 = 已披露（海康 7 月底披露）
- 中报业务分部/毛利率/研发/指引最全在新闻稿：`https://www.p5w.net/roll/cj/...` 用 urllib + 正则去 script/style/标签 直接解析（web_extract 不可用时的替代路径）52周高低可用亿牛网 `eniu.com/gu/sh{code}` 确认（拓荆 2024-09-26 历史最低 46.14 元）。

### 同花顺 F10 页面内嵌 JSON 抓取（2026-08 三生国健实战）

`basic.10jqka.com.cn/{code}/worth.html`（盈利预测）和 `holder.html`（股东户数）**直接抓取是 GBK 乱码**，但页面内嵌 JSON 数组可解析出关键数据：

```python
# worth.html 盈利预测：页面内嵌 [["2019","0.43","2.29","SJ"],...] 形式的历史 EPS/净利序列
# 另有："预测2026每股收益 0.75 元 同比降 84.04%"（含当年一致预期 EPS 与净利）
# holder.html 股东户数：[["2026-06-30","20589","53.10","股东人数"],...]（日期/户数/户均持股/标签）
```

**用法**：盈利预测页拿券商一致预期（2026E 净利/EPS）——BD 一次性收入污染的创新药企必须靠它做盈利正常化锚点；holder 页拿股东户数序列——半年翻倍 = 散户化筹码信号（芒格风险清单）。抓取时先 `re.sub` 去标签再在 `<script>` 内找 `[[...]]` 数组，用 `json.loads` 解析。

### ⚠️ 东财报表接口数值列是字符串（2026-08 三生国健实战）

`ak.stock_balance_sheet_by_report_em` / `stock_cash_flow_sheet_by_report_em` / `stock_profit_sheet_by_report_em` 的数值列**可能是 str 类型**（直接 `v/1e8` 报 `unsupported operand type(s) for /: 'str' and 'float'`）。必须统一 to_num 转换后再算：

```python
def to_num(x):
    try:
        if x is None: return None
        if isinstance(x, str):
            x = x.replace(',','')
            if x in ('', '--', 'None', 'nan'): return None
            return float(x)
        return float(x)
    except: return None
```

另外注意 `CONSTRUCT_LONGASSET`（资本开支）字段在该接口常缺失——CapEx 需用固定资产变动或新闻估算。

### ✅ 东财 datacenter API 直连兜底 + 研报PDF提取（2026-09 恒立液压 601100 实战）

当 akshare 东财封装（`stock_balance_sheet_by_report_em` / `stock_cash_flow_sheet_by_yearly_em` / `stock_fhps_detail_em`）连续报 `'NoneType' object is not subscriptable`、同花顺兜底接口也失效时，**直连东财 datacenter API 一次成功**，是 A 股报表+分红的最终兜底：

```
https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName={报表名}&columns=ALL&filter=(SECUCODE%3D%22{code}.SH%22)&pageNumber=1&pageSize=40&sortTypes=-1&sortColumns=REPORT_DATE&source=HSF10&client=PC
```

| 报表名 | 内容 | 关键字段 |
|---|---|---|
| RPT_F10_FINANCE_MAINFINADATA | 主要指标全序列（含 YoY） | EPSJB/BPS/ROEJQ/XSMLL/ZCFZL/MGJYXJJE + `*TZ` 系列增速列 |
| RPT_F10_FINANCE_GINCOME | 利润表明细 | OPERATE_INCOME/COST/SALE_EXPENSE/MANAGE_EXPENSE/RESEARCH_EXPENSE/FINANCE_EXPENSE/PARENT_NETPROFIT/DEDUCT_PARENT_NETPROFIT |
| RPT_F10_FINANCE_GBALANCE | 资产负债表 | MONETARYFUNDS/INVENTORY/TOTAL_PARENT_EQUITY/CIP — ⚠️ 在建工程字段名是 **CIP** 不是 CONSTRUCT_LONGASSET |
| RPT_F10_FINANCE_GCASHFLOW | 现金流量表 | NETCASH_OPERATE/INVEST/FINANCE（无购建固定字段时 CapEx 用 BS 固定资产变动估算） |
| RPT_SHAREBONUS_DET | 分红送配全史 | PRETAX_BONUS_RMB=**每10股派息**（年报+中期+特别股息各一条独立记录，全年 DPS 须累加） |

陷阱：①数值单位是**元**，需 /1e8 转亿；②filter 的 SECUCODE 用 `601100.SH` 格式且须 urlencode（`%3D` `%22`）；③REPORT_DATE 是 Timestamp 字符串，先 `astype(str)` 再排序取尾部；④RPT_SHAREBONUS_DET 的 filter 用 `SECURITY_CODE%3D%22601100%22`（不带 .SH 后缀）。分页字段 pageNumber/pageSize 必须带，缺了部分报表返回空。

**券商研报全文 = 盈利预测金矿（一致预期一键拿）**：
- 列表：`https://reportapi.eastmoney.com/report/list?pageSize=60&beginTime=2026-08-01&endTime=2026-09-03&pageNo=1&qType=0&code=601100`（A股用 `code=` 参数；港股 01209 返回空 → 改用 keywords=公司名 urlencode）
- 下载：`https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf` → `pdftotext -layout` 提取
- 用途：中报点评研报含**分产品/分部增速**（油缸泵阀各档同比）、**剔除一次性因素后的真实增速测算**（东吴/国信口径）、**多券商 2026-28E 净利列表** → 直接算一致预期与 PE 区间（恒立：四家券商 32.8/33.7/34.1/36.0 亿）。比 web_search 拼摘要高效一个量级，且是"增收不增利"拆解的唯一可靠来源。

### ⚠️ "增收不增利"三查清单（2026-09 恒立液压实战：营收+32% 净利+0.5% 必查）

A股中报营收大增但净利停滞/下滑时，按序排查三因再下结论，禁止直接写"盈利能力恶化"：

1. **汇兑损失（财务费用反转）**——人民币快速升值时，有美元资产/出口/海外工厂的制造公司（恒立墨西哥、福耀玻璃 2026H1 汇兑损失 8 亿等）财务费用从负（净收益）反转为正（净损失）。判别信号：利润表 FINANCE_EXPENSE 同比大幅恶化 + 新闻含"汇兑"。恒立 2026H1：财务费用 -2.67亿→+1.95亿（反转 4.6 亿 ≈ 吞掉全部利润增量），汇兑净损失 2.78 亿。
2. **新产能爬坡折旧+低产能利用率**——固定资产/在建跳增后新厂投产首年拖累毛利率；**单季毛利率环比回升 = 爬坡尾声的最早信号**（恒立 Q2'26 单季毛利率 39.89% 环比 +1.32pct）。
3. **费用前置**——销售费用 +40% 拓市场、研发/管理投入加速（扩张期特征非恶化）。

⚠️ 关键动作：**找券商中报点评的"剔除汇兑后经营性净利增速"**（东吴恒立测算：剔除后 +38%）——这是区分"报表利润停滞"与"主业真实弹性"的唯一可靠口径，报告正文必须同时呈现表观增速与剔除后增速两个数字。

## Effective Search Query Patterns

After multiple sessions of A-share analysis, these query patterns produce the most useful snippets:

### Reliable Patterns (high snippet yield)

| Pattern | Example | What You Get |
|---------|---------|-------------|
| `"{公司}" "{代码}" "{年份}年报 净利润"` | `"明月镜片" "301101" "2025年年报 净利润"` | Exact annual NI numbers from news sites |
| `"{代码} EPS 每股收益 每股净资产"` | `301101 EPS 每股收益 每股净资产` | BVPS and EPS from Futu/新浪 snippets |
| `"{代码} 关键财务指标" site:futunn.com` | `301101 关键财务指标 site:futunn.com` | BVPS, ROE, net margin from Futu |
| `"{公司}" "毛利率" "{年份}" "{年份}"` | `"明月镜片" "毛利率" "2024" "2025"` | Gross margin trends |
| `"{公司}" "{年份}H1" OR "上半年" 营收 净利润` | `"明月镜片" "2025年上半" 营收 净利润` | Half-year breakdowns |
| `"{公司}" "镜片业务" "营收" "同比"` | `"明月镜片" "镜片业务" "营收"` | Segment-level revenue in analyst report snippets |
| `"{代码}" "ROE" OR "净资产收益率"` | `301101 ROE 净资产收益率` | ROE values from multiple sources |

### Low-Yield Patterns (avoid)

| Pattern | Why It Fails |
|---------|-------------|
| `"{代码}" "资产负债表" "总资产"` | Chinese search snippets almost never contain full B/S data |
| `"{代码}" "经营现金流" "每股"` | OCF data rarely appears in snippets except in PDF reports |
| `"{代码}" "2022" "2023" "2024" "营收" "净利润"` | Multi-year queries in one search dilute relevance; search one year at a time |
| `site:kancaibao.com "{代码}"` | 看财报's search-filtered pages don't index well; use eniu.com instead |

### When Web Search Fails: Estimation Strategy

If 6+ rounds of web_search still don't yield exact numbers for all years:

1. **Anchor on confirmed data points** (e.g., 2025 NI=1.93亿 from news, BVPS=9.02 from Futu)
2. **Backfill using YoY growth rates** mentioned in earnings snippets (e.g., "H1 net profit +7.35% YoY")
3. **Use net margin consistency**: if overall margins are stable (~24%), revenue can be estimated from NI
4. **Flag estimates clearly** in reports: mark estimated figures with "≈" and note the estimation method

## Cross-Validation Formula

```
Market cap = 股价 × 总股本
PE = 股价 / EPS
PB = 股价 / BVPS = 市净率
ROE = EPS / BVPS × 100%

Verify: PE × ROE/100 ≈ PB
Example: 51 × 0.17 ≈ 8.7 ✓
```

## Common Snippet Patterns

Chinese financial snippets are less structured than English ones. You often get:
- "营收109.41亿元，同比上升16.52%" → extract 109.41 and 16.52%
- "归母净利润27.34亿元，同比上升8.99%" → extract 27.34 and 8.99%
- "拟10派5.60元" → dividend = 0.56/share

The `kancaibao.com` site is the most reliable for exact historical annual data in one shot.

## Balance Sheet Estimation

Chinese search snippets rarely contain full balance sheet data. Estimation approach:
- **Total assets**: from credit rating reports or "境外资产占比" hints (e.g., "境外资产26.99亿占总资产13.16%" → total ≈ 205亿)
- **Cash**: from quarterly reports mentioning "货币资金" (e.g., "货币资金79.39亿元")
- **Debt ratio**: qualitative ("极低的资产负债率") → assume 25-35% for cash-rich manufacturers
- **BVPS**: from ROE and EPS (BVPS = EPS / ROE × 100)
- **OCF**: from trend mentions ("经营现金流同比下降19.77%")
- **CapEx**: from credit rating reports ("购建固定资产...支付17.42亿元")

## 东财 datacenter 直连 API：akshare 东财封装连环失效时的首选兜底（2026-09 恒立液压 601100 实战）

`ak.stock_balance_sheet_by_report_em` / `stock_cash_flow_sheet_by_yearly_em` / `stock_cash_flow_sheet_by_report_em` / `stock_fhps_detail_em` 全部抛 `'NoneType' object is not subscriptable`（封装层不稳定）时，**不要再反复重试 akshare，直接打东财 datacenter HTTP API**——一次成型、字段齐全、含中报期：

```python
import urllib.request, json

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")

def get_rows(report, secucode="601100.SH", pagesize=40):
    url = (f'https://datacenter.eastmoney.com/securities/api/data/v1/get'
           f'?reportName={report}&columns=ALL'
           f'&filter=(SECUCODE%3D%22{secucode}%22)'
           f'&pageNumber=1&pageSize={pagesize}&sortTypes=-1&sortColumns=REPORT_DATE&source=HSF10&client=PC')
    return json.loads(fetch(url)).get("result", {}).get("data", [])
```

**已实测报表与关键字段（2026-09）：**

| reportName | 内容 | 关键字段 |
|---|---|---|
| `RPT_F10_FINANCE_MAINFINADATA` | 主要指标（全报告期含中报） | EPSJB/EPSKCJB/BPS/MGJYXJJE(每股OCF)/ROEJQ/XSMLL(毛利率)/XSJLL(净利率)/ZCFZL(负债率)/…TZ(同比) |
| `RPT_F10_FINANCE_GINCOME` | 利润表 | OPERATE_INCOME/OPERATE_COST/SALE_EXPENSE/MANAGE_EXPENSE/RESEARCH_EXPENSE/**FINANCE_EXPENSE(财务费用)**/OPERATE_PROFIT/PARENT_NETPROFIT/DEDUCT_PARENT_NETPROFIT |
| `RPT_F10_FINANCE_GBALANCE` | 资产负债表 | MONETARYFUNDS/ACCOUNTS_RECE/INVENTORY/FIXED_ASSET/**CIP(在建工程)**/TOTAL_ASSETS/TOTAL_LIABILITIES/TOTAL_PARENT_EQUITY/MINORITY_EQUITY（⚠️ 无 CONSTRUCT_LONGASSET 字段，capex 需用券商预测表或固定资产+在建变动估） |
| `RPT_F10_FINANCE_GCASHFLOW` | 现金流量表 | NETCASH_OPERATE/NETCASH_INVEST/NETCASH_FINANCE（无单独 capex 字段） |
| `RPT_SHAREBONUS_DET` | 分红送配历史 | PRETAX_BONUS_RMB(每10股派)/REPORT_DATE/EQUITY_RECORD_DATE/EX_DIVIDEND_DATE/ASSIGN_PROGRESS——**中期分红独立成行**，全年 DPS = 年报行 + 中期行 |

⚠️ 陷阱：
- 数值列单位=元（÷1e8 转亿）；REPORT_DATE 是 Timestamp，需 astype(str) 后 sort_values 再 tail（东财接口不保证排序）；
- **投资净流出 ≠ capex**：含理财/结构性存款申赎（恒立 2026H1 投资净流出 23.98亿 但货币资金反增 ~14亿 = 现金管理；真实 capex 参考券商盈利预测表的"资本开支"行）；
- **港股中报（06-30）在 EM 接口常滞后**：`stock_financial_hk_analysis_indicator_em` 可能只到上年年报（华润万象生活 2026H1 已披露仍停在 2025-12-31）→ 直接抓 观点网 guandian.cn/article/YYYYMMDD/{id}.html 正文（urllib 可抓，含分航道收入/毛利率/派息精确数）。

### 券商研报 PDF 直链（A股/港股通用，2026-09 验证）

1. 搜研报列表：`https://reportapi.eastmoney.com/report/list?pageSize=60&beginTime={YYYY-MM-DD}&endTime={YYYY-MM-DD}&pageNo=1&qType=0&code={6位代码}`（⚠️ 用 `code=`，`rcode=` 返回 0 行）→ 每条含 publishDate/orgSName/title/sRatingName/infoCode
2. 下 PDF：`https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf`（urllib + UA 即可，len > 10KB 为有效）
3. `pdftotext -layout {pdf} -` → 拿到中报点评全文 + **盈利预测表含 capex/FCFF/每股OCF/ROE 多年预测**——券商 capex 预测是 FCF 建模的最佳输入，东财报表接口反而没有（恒立：国信预测 capex 2025A 9.93亿/2026E 11.2亿，直接校准了 DCF base FCF）

## 东财 datacenter API 直连（akshare 封装 + 同花顺双双失效时的终极兜底，2026-09 恒立液压 601100 实战）

当 `stock_balance_sheet_by_report_em` / `stock_cash_flow_sheet_by_report_em` / `stock_fhps_detail_em` 全部报 `'NoneType' object is not subscriptable`，且同花顺现金流接口（`stock_financial_cash_ths` KeyError 'flashData'）与分红接口（`stock_fhps_detail_ths` XMLSyntaxError）也失效时——**直连东财 datacenter API 一次成功**，不要反复重试 akshare 封装：

```
https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName={REPORT}&columns=ALL&filter=(SECUCODE%3D%22{SECUCODE}%22)&pageNumber=1&pageSize=40&sortTypes=-1&sortColumns=REPORT_DATE&source=HSF10&client=PC
```

- SECUCODE 格式 `601100.SH`（带交易所后缀）；返回 `result.data` 按报告期**倒序**（新→旧），直接 `[0]` 即最新一期，无需 sort
- 数值单位是**元**，÷1e8 = 亿
- 已实测可用的报表（2026-09 恒立液压）：

| REPORT_NAME | 内容 | 关键字段（实测） |
|------|------|------|
| `RPT_F10_FINANCE_MAINFINADATA` | 主要财务指标全序列 | EPSJB(基本EPS)/EPSKCJB(扣非)/BPS/MGJYXJJE(每股OCF)/ROEJQ(加权ROE)/XSMLL(毛利率)/XSJLL(净利率)/ZCFZL(负债率)/TOTALOPERATEREVETZ(营收YoY)/PARENTNETPROFITTZ(净利YoY)。⚠️ 该报表绝对额字段(TOTAL_OPERATE_INCOME/PARENT_NETPROFIT)为 None——绝对额去 GINCOME 拿 |
| `RPT_F10_FINANCE_GINCOME` | 利润表明细 | OPERATE_INCOME/OPERATE_COST/SALE_EXPENSE/MANAGE_EXPENSE/RESEARCH_EXPENSE/**FINANCE_EXPENSE**(汇兑诊断看它)/OPERATE_PROFIT/PARENT_NETPROFIT/DEDUCT_PARENT_NETPROFIT |
| `RPT_F10_FINANCE_GBALANCE` | 资产负债表 | MONETARYFUNDS/ACCOUNTS_RECE/INVENTORY/FIXED_ASSET/**CIP（在建工程字段叫 CIP，不叫 CONSTRUCT_LONGASSET）**/INTANGIBLE_ASSET/GOODWILL/TOTAL_ASSETS/TOTAL_LIABILITIES/TOTAL_PARENT_EQUITY/MINORITY_EQUITY/ACCOUNTS_PAYABLE/CONTRACT_LIAB |
| `RPT_F10_FINANCE_GCASHFLOW` | 现金流量表 | NETCASH_OPERATE/NETCASH_INVEST/NETCASH_FINANCE。⚠️ 投资净流出含理财/大额存单购买（恒立 2026H1 投资净流出 23.98亿 但固定资产仅 +0.3亿），**不可直接当 capex**——capex 用研报预测表或固定资产+在建变动估算 |
| `RPT_SHAREBONUS_DET` | 分红送配历史 | PRETAX_BONUS_RMB(每10股派息)/REPORT_DATE/PLAN_NOTICE_DATE/ASSIGN_PROGRESS(董事会决议通过→实施分配)/EX_DIVIDEND_DATE。中报+年报分红为**独立记录**，全年 DPS = 两笔之和（恒立 2025：年报 0.56 + 中期 0.30 = 0.86 元） |

## 东财个股研报搜索 + PDF 下载（券商一致预期/中报点评一次拿全，2026-09 恒立实测）

中报/年报披露后要拿券商点评与 2026E 一致预期，不需要逐篇搜新闻：

```
https://reportapi.eastmoney.com/report/list?pageSize=60&beginTime=2026-08-01&endTime=2026-09-03&pageNo=1&qType=0&code=601100
```

- `code={六位代码}` 直接返回该股全部研报（按 publishDate 倒序），字段：orgSName/title/publishDate/infoCode/sRatingName
- 研报全文 PDF：`https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf`（urllib + UA 直下），`pdftotext -layout` 提取
- **盈利预测表、管理层指引、分产品增速、剔除一次性因素测算全在 PDF 里**——恒立案例：中报 8/25 盘后披露，8/25-8/28 国金/招银/中邮/东吴/国信 5 份点评一次拿全，含 2026E 净利一致预期（32.8-36 亿 → PE ~39x）与"剔除汇兑后经营净利 +38%"的券商测算
- 可比公司估值表也在研报尾部（如恒立 vs 三一 16x/柳工 8x）——同业对比表直接引用，省一轮搜索
