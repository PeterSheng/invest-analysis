# SEC 一手文件取证配方（8-K / 10-Q / 指引轨迹 / 重析轮审计）

适用：美股四大师分析的数据包构建，尤其是「重析轮」——旧报告结论必须用一手文件证伪，
而不是在旧数字上叠加新价格。本配方为 2026-11 Zoetis（ZTS）轮实测沉淀，全部步骤均成功取数。

---

## 1. CIK 必须查表，不能猜

```python
# 1) 官方 ticker→CIK 映射（唯一权威入口）
h = get("https://www.sec.gov/files/company_tickers.json")
j = json.loads(h)
[v for v in j.values() if v["ticker"] == "ZTS"]
# → {'cik_str': 1555280, 'ticker': 'ZTS', 'title': 'Zoetis Inc.'}
```

**坑**：先用猜的 CIK（如 1553714）拉 `companyfacts`，会返回**另一家公司**（内部人持股申报）的
JSON，看起来"有数据"但科目全错。凡 `companyfacts` 返回空串或科目缺失，第一嫌疑是 CIK 错，
第二才是限流——先回查 ticker 表。

Header 统一：`User-Agent: FinancialAnalysis research contact@example.com`（SEC 要求可识别 UA）。

---

## 2. 定位 8-K / 10-Q：submissions → index.json → exhibit

```python
# 2) 全部申报清单（含 form / filingDate / accessionNumber）
sub = json.loads(get("https://data.sec.gov/submissions/CIK0001555280.json"))
recent = sub["filings"]["recent"]
# 按 form=8-K 过滤，取目标日期的 accessionNumber

# 3) 一次 8-K 的目录，用来发现 exhibit 文件名
idx = json.loads(get(f"https://www.sec.gov/Archives/edgar/data/1555280/{acc_nodash}/index.json"))
[it["name"] for it in idx["directory"]["item"]]
# 例：['exhibit99q32026.htm', 'zts-20261105.htm', 'R1.htm', ...]
```

**命名不统一，必须靠 index.json 发现**，不要拼文件名：
- `exhibit99q32026.htm`（季度财报新闻稿）
- `exhibit9913q2026dividendpr.htm`（分红公告，同日 8-K 会混进来）
- 10-Q 主文档形如 `zts-20260930.htm`，**accession 与同期的 8-K 不同**——用 8-K 的 accession 拼 10-Q
  路径会 404，必须从 submissions 取 10-Q 自己的 accession。

---

## 3. 表格类 exhibit：必须走 tr/td 行解析

**失败过的做法**：整篇 `re.sub('<[^>]+>',' ')` 去标签后搜关键词 → 返回空。
原因：新闻稿 exhibit 用嵌套 `<font>` 单元格 + 内嵌 base64 图片（800KB+），扁平化后单元格值
被压成一串无边界文本，`Dermatology`/`Companion` 等行首词被吃掉。

**可用做法**：先按 `<tr>` 切行，再按 `<td>` 切单元格，逐格去标签，只保留含数字的行：

```python
def rows(html):
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        line = " | ".join(c for c in cells if c)
        if any(ch.isdigit() for ch in line):
            out.append(line)
    return out
```

**坑**：10-Q 的 XBRL 元数据（`us-gaap:*Member`、context id）会把产品分部的数字重复几遍，
纯关键词 grep 命中的第一段往往是元数据而非 MD&A 表。用 `rows()` 输出后人工筛，或取命中位置
±800 字符窗口读上下文。

10-Q 里值得锁定的关键词：`Dermatology`（产品收入表）、`securities class action`（集体诉讼案号/首席原告/
class period）、`Prosecutor` / `antitrust`（监管尾部风险）、`Short-term borrowings` / `Current portion
of long-term debt`（有息负债穿透）。

---

## 4. 指引轨迹表：管理层可信度的一级证据

每份季度 8-K 的新闻稿都带 `Prior Guidance / Current Guidance` 对照表（行：Revenue / Adjusted net
income / Adjusted diluted EPS / Reported diluted EPS）。**把全年 4 次（初始 + Q1 + Q2 + Q3）都拉出来，
做成四点表 + 中值累计变动**，这是芒格视角最锋利的一件武器，也是判断"下修是一次性还是趋势"的唯一硬证据。

ZTS 2026 实测（worked example，可直接套结构）：

| 时点 | 营收指引 | 有机 | 调整后净利 | 调整后 EPS | 报告 EPS |
|---|---|---|---|---|---|
| 2026-02-12 初始 | 9.825–10.025B | +3~+5% | 2.975–3.025B | 7.00–7.10 | 6.65–6.75 |
| 2026-05-07 Q1 | 9.68–9.96B | +2~+5% | 2.87–2.95B | 6.85–7.00 | 6.35–6.50 |
| 2026-08-06 Q2 | 9.12–9.32B | −3~−1% | 2.57–2.62B | 6.15–6.25 | 5.55–5.65 |
| 2026-11-05 Q3 | 9.22–9.32B | −2~−1% | 2.60–2.64B | 6.25–6.35 | 5.50–5.60 |

中值累计：营收 **−6.6%**、调整后 EPS **−10.6%**；增速叙事从 +4% 翻到 −1.5%。
判读规则：**下修 ≥2 次即扣管理层可信度**；若某一季出现"口头 raise"（EPS 区间上调 10 分钱）
但营收仍在下移，按"化妆式上调"处理，不给分。

配套读法：Q3 的"EPS 上调但有机净利仍 −7%"= 缩股买 EPS（股本 −4%），要单列出来，
不能算经营改善。

---

## 5. 电话会记录（定性部分的唯一来源）

路径：`fool.com/earnings/call-transcripts/YYYY/MM/DD/<company>-<ticker>-qN-2026-earnings-call-transcript/`
（可用 urllib + 桌面 UA 直取，正文为纯文本）。

必抓五段，直接决定 01/03/04 三篇的成色：
1. **价格 vs 销量拆分**（"−1% organic = −1% price, flat volume"）→ 定价权是否还在。
2. **份额损失的具体点数**（"US derm share loss slowed to 4pp from 7pp"）→ 让利是否有效。
3. **下一年度口径**（"we will not assume improvements in macro... competitive dynamics throughout
   most of the year"）→ 2027 是第二下滑年的官方措辞。
4. **资本配置优先级**（R&D/bolt-on M&A 优先、余下返还）→ 回购是纪律还是维稳。
5. **单季计提/减值**（如 IPR&D impairment $89M）→ GAAP 与 adjusted 的桥。

---

## 6. 重析轮三查（旧报告不审计就不得继承结论）

这是本配方最重要的一节。**旧报告存在 ≠ 结论可用**。

1. **财年标签审计**：把旧报告的收入/净利/EPS 序列与 stockanalysis 10 年表逐年对齐。
   Zoetis 202607 报告把 FY2023（$8.544B / $2.34B / EPS 5.07）标成 "FY2025"，据此得出
   "利润仍在增长 +10.9%、跌幅几乎 100% 来自估值压缩"——**错标两年，整段结论作废**。
   错标 ≥1 年的旧报告，其 CAGR、ROE、安全边际全部需要重算，不得引用。
2. **指引轨迹表**（第 4 节）：旧报告若未做，重析轮必须补上。
3. **击球区重定基**——"**击球区到了，球变了**"：现价跌进旧区间不等于触发。
   若同期 EPS 指引中值下移 >5%，旧区间必须按下移后 EPS 重算。
   Zoetis 旧区间 $70-80 在 $79.85 被触及，但 FY26 adj EPS 中值已 $7.05→$6.30（−10.6%），
   区间应系统性下移，而不是"触发了就买"。

---

## 7. 资产轻型药企的估值双基（报告口径 vs 所有者收益）

同一家公司、同一 WACC 10%，两个口径可以差 25%：

| 口径 | 公式 | ZTS 2026-11 |
|---|---|---|
| 报告口径 | FCF = OCF 2,726 − capex 498 = **2,228** | IV 基准 **$58.9** |
| 所有者收益 | NI 2,507 + D&A 490 − 维护性 capex 300~400 = **2,597~2,697** | IV **$71.7~75.2** |

现价 $79.85 卡在两个口径之上。**处理纪律**：
- 两个口径都摆出来，绝不择一了事；
- 明确点名唯一的会计自变量——"capex 里维护性占比"（ZTS capex 仅营收 5.2%、D&A≈capex）；
- 反向 DCF 交叉验证：现价隐含 10 年 FCF 增速 +5.7%/年 vs 实际 FY21→TTM +5.1%——
  **市场没为基本面恶化打任何折**，这才是"看起来 13x PE 很便宜"的真相。

---

## 8. 行情/可比数据的取数顺序（实测 2026-11）

1. `qt.gtimg.cn/q=usZTS,usIDXX,usELAN` —— 现价/涨跌/52 周/PE 最快；字段下标（实测）：
   `[3]`现价 `[4]`昨收 `[5]`开盘 `[32]`涨跌% `[39]`PE(TTM) `[41]`52周高 `[42]`52周低 `[44]`总市值 `[45]`流通市值。
2. `stockanalysis.com/stocks/<ticker>/financials/...` —— 10 年报表序列（营收/毛利/营业利润/净利/EPS/
   分部/现金/总债务/OCF/capex/FCF/D&A），用整页去标签后按指标名定位，一次能取齐 6 年。
3. `stockanalysis.com/stocks/<ticker>/history/?range=1Y` —— 日线；腾讯 `usfqkline` 接口对美股
   实测只回最后 1 根 bar，历史路径优先用 stockanalysis。
4. `web_extract` 在 ddgs 后端下只能搜索，正文用 urllib + 桌面 UA 直取。

---

## 9. 输出映射（写进 00-数据包的最小集）

- 双价格锚：收盘价（主）/ 盘中或盘后价（辅），并写清"分析日 vs 价格截至日"。
- 市值、净债（= 总债务 − 现金 − 短期投资）、EV、EV/EBITDA、EV/FCF。
- 分部 × 地区的收入表 + 有机增速 + 价格/销量拆分。
- 指引轨迹表（4 点）。
- 产品级收入表（若 10-Q 有）：找出"哪一半在失血"，这决定护城河评级。
- 回购：股数 × 均价 × 金额 vs 现价 —— 资本配置评分的关键证据（ZTS 9M 均价 $95.4 vs 现价 $79.5）。
- 法律：案号 / 首席原告 / class period / 阶段（立案→修订→集体认证）。
