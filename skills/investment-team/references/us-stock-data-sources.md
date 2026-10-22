# 美股数据源实测清单（2026-08 Netflix/NFLX 实战验证）

> 美股财务数据**首选直接抓 stockanalysis.com**（urllib 即可，无需 web_extract/browser）。
> 之前"美股财务靠 web_search 拼新闻"是低效路径——本文件给出完整配方。

## 1. 首选：stockanalysis.com 直接抓取

URL 模式（ticker 小写）：

| 页面 | URL |
|------|-----|
| 利润表 | `https://stockanalysis.com/stocks/{ticker}/financials/` |
| 资产负债表 | `https://stockanalysis.com/stocks/{ticker}/financials/balance-sheet/` |
| 现金流量表 | `https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/` |
| 比率 | `https://stockanalysis.com/stocks/{ticker}/financials/ratios/` |
| **概览页（行情快照）** | `https://stockanalysis.com/stocks/{ticker}/` —— 52周高低 / Beta / 分析师评级与目标价 / 下次财报日 / 员工数 / 行业 / 交易所 |
| **季度页（周期拐点检测）** | 上述任一 URL 加 `?p=quarterly`（如 `.../financials/?p=quarterly`）——返回**逐季序列（最新在前）+ 各季 YoY 增速**，是判断周期位置/拐点的一手来源（POOL 实战：2023Q1 -14.6% → 2026Q2 +2.2%，三年下行后首次连续正增长只能从季度页确认，年度页和 web_search 都拿不到） |

**季度页实测要点（POOL 2026-08 验证）**：
- income / cash-flow / ratios 三页加 `?p=quarterly` 正常解析；**balance-sheet 季度页解析为空**——季度资产负债表不可用，用年度页替代
- 季度页列顺序 = 最新季在前（如 2026Q2 | 2026Q1 | 2025Q4 | ...），无需再猜列序
- 单季 EPS YoY 增速列在 `EPS Growth` 行；单季毛利率/净利率/营业利润率同行给出——**判断"收入企稳但利润未确认拐点"（POOL 2026H1：收入 +2.2%/+6.2% 但净利仍 -2.7%）全靠这一页**

实测要点（NFLX 2026-08 验证）：
- `urllib.request` + 浏览器 UA 头即返回 200，无需 cookie/JS
- **列结构**：`TTM | FY2025 | FY2024 | FY2023 | FY2022 | FY2021`（TTM = 最近季度末，如 Jun '26）
- **单位**：$M（百万美元）
- **列序确认法**：建模前先用已知历史值核对列序（LULU：最旧列营收 $6,257M = FY2021 真实值；ADBE：$15,785M = FY2021）——确认 TTM 在最左、年份从新到旧，防止 FY 标签错位导致整套建模全错。零售股财年以"结束所在日历月"命名（LULU FY2025 = 2026-02-01 止）
- **年度净利跳增必查季度**：年度净利同比 >20% 时，把季度页净利按财年求和验证（ADBE FY2025 +28% 之谜：Q1'24 净利仅 $620M = Figma 终止相关税项低基数 → FY2024 被压低，FY2025 是低基数修复而非经营突变）。季度页同时暴露被年度平滑掉的单季崩塌（LULU Q1'26 净利 -38%、毛利率 -4.2pct、营业利润率 -7.3pct——仅看年度页会漏掉拐点）
- **概览页提取配方**：`https://stockanalysis.com/stocks/{ticker}/` 去 script/style 后正则搜 "52-Week Range" 附近 120 字符，一次拿全行情快照（52周高低/Beta/分析师评级与目标价/下次财报日/员工数），写报告头部所需全在这
- **解析**：正则 `<table>` → `<tr>` → 每行 = `指标名 + 值数组`；跳过表头行（含 "Fiscal Year"/"Period Ending" 的行）；cell 内指标名与增速可能同格（如 `Revenue    Revenue Growth`），取第一个
- **ratios 页一次拿全估值口径**：Market Cap、Last Close Price、PE、Forward PE、PEG、PB、PS、P/FCF、FCF Yield、ROE、ROA、ROIC、D/E、Net Debt、Buyback Yield、资产周转率——比手动算省一半时间
- 分部营收也在利润表页（如 Netflix 的 UCAN/EMEA/LATAM/APAC 分列）

抓取模板：

```python
import urllib.request, re, html as htmllib
def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", errors="ignore")

def parse_tables(html_text):
    tables = re.findall(r'<table.*?</table>', html_text, re.S)
    result = {}
    for t in tables:
        rows = re.findall(r'<tr.*?</tr>', t, re.S)
        header = None
        for r in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)
            cells = [htmllib.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in cells]
            if not cells: continue
            if any('Fiscal Year' in c or 'Period Ending' in c for c in cells):
                header = cells; continue
            if header and len(cells) >= len(header) - 1:
                result[cells[0]] = cells[1:len(header)]
    return result
```

**交叉验证配方**：
- Last Close Price（ratios 页）↔ 腾讯 API `us{ticker}` 字段[3]（⚠ 时区：北京时间晚上 = 美东未开盘，取上一交易日收盘；⚠ 响应为 **GBK 编码**：`resp.read().decode('gbk')`，按 UTF-8 解码会乱码——PFE 2026-10 实战）
- Market Cap（ratios 页，$M）↔ 腾讯 API 字段[45]（亿 USD）
- ⚠ 腾讯美股字段[46] **不是 PB**（2026-08 LULU/ADBE 实测返回公司名）——PB 一律以 ratios 页为准；字段[45] 市值（亿 USD）实测可靠（LULU $13.1B / ADBE $108.2B 与 ratios 页一致）
- PE = 价格 ÷ TTM EPS ↔ ratios 页 PE ↔ 腾讯字段[39]，三处一致才采信
- 市值 ÷ 价格 = 股本（NFLX：$325.8B ÷ $78.24 ≈ 41.6 亿股，与回购史吻合）

## 2. 美股特有陷阱（Netflix 实战）

| 陷阱 | 处理 |
|------|------|
| **自定义 DCF 模型的 $M/$B 单位因子** | `dupont_analysis.py` 模板里 `iv = eq × 1000 / shares` 只适用于 **$B 单位**输入（$B→$M 转换）。**直接从 stockanalysis 拿 $M 数据建自定义模型时，equity 也是 $M，`iv = eq / shares_m`（百万/百万 = 美元/股），多乘 1000 会让 IV 虚高 1000 倍**（POOL 实战：$159,269 vs 正确 $159）。同理 OCF/股 = `ocf_m / shares_m`，不是 ×1000。跑完先做合理性检查：IV 应与股价同量级 |
| **ROE 均值回归公式的单位一致性** | `pb_norm = roe_norm / roe_now × pb_now` 中两数必须**同口径**（都用百分数，如 25/31.25）。混用小数（0.25）和百分数（31.25）会让 PB 收缩到 0.04x 的荒谬值（POOL 实战：算出股价 $2，修正后 $150 才合理） |
| **拆股口径** | NFLX 2025-10 做过 1:10 拆股，所有历史 EPS/价格须确认是否拆股后口径。快速判断：52 周高低价与现价是否同量级（拆股前 $900+ → 拆股后 $90） |
| **一次性收益污染** | Netflix 2026 WBD 竞购战退出后获 Paramount $28 亿分手费，或计入 2026 净利 → TTM 净利 $13.65B 可能含 $2.8B 水分 → 表面 PE 24.6x vs 核心 PE ~30x。**必须做"剔除一次性收益"敏感性**，用核心口径做估值锚 |
| **内容资产计入无形资产** | Netflix 内容资产 $33.8B 为最大资产项 → 有形净资产为负（-$3.7B）、资产周转率偏高（0.83，轻资产公司本应 ~0.5）。DuPont 解读必须说明该结构，并用 ROIC（34.7%）交叉验证 ROE 真实性 |
| **订阅数估算** | 服务类公司若财报不强调订阅数（Netflix 2025 起以收入/engagement 为核心 KPI），用 ARPU 反推：`平均订阅 = TTM 营收 ÷ (ARPU × 12)`。Netflix ARPU ~$12-12.5/月 → ~3.3-3.4 亿。报告中标注"估" |
| **⚠️ 四页数据单位是 $M，不是 $B** | stockanalysis.com 全部单位 $M。dupont_analysis.py 模板硬编码 $B 转换（`eq*1000/shares`）。**$M 口径下：`IV = eq / shares_m`、`OCF/股 = ocf / shares_m`**。POOL 实战（2026-08）：误用 `*1000` → IV=$159,269、OCF/EPS=540x。跑完自检三件套：IV 与股价同量级、资产周转率 0.5-1.5、OCF/EPS 0.5-2.5x |
| **分销商库存周期（POOL 类）** | 批发分销商 OCF/NI 随库存周期大幅摆动（POOL：0.49x→1.71x→0.90x——补库时低、去库存时高），**单年 OCF/NI 不可信，看 5 年均值**（POOL ~1.06x 健康）。DCF base FCF 用归一化均值（POOL $450M = 5 年均值 $491M 打 92 折），不能用 TTM 谷底值（$301M，会低估）也不能用收缩释放峰值（$828M，会高估） |
| **非美列报公司：四页数据单位是财报货币（HK$M 等），不是 USD** | **FUTU 2026-08 实战**：富途纳斯达克上市但以港元列报，四页单位全部 HK$M（TTM 净利 11,116 = HK$111.2亿 = $14.3亿，不是 $111亿）。检测链（遇到"净利巨大 + PE 对不上"必做）：① `NI ÷ EPS = 股本`（11,116/78.65 = 141.3M = ADS 数，与市值÷价格反推 1.4 亿一致）→ 每股数据是"每股 ADS × 财报货币"；② `价格 ÷ PE(TTM) = 隐含 EPS`（115.81/11.55 = $10.03 ≈ HK$78.65/7.8）→ 汇率换算吻合即确认货币；③ **用已知真实值锚定**（FY2024 NI HK$5,443M ÷ 7.8 = $698M = 富途 2024 实际净利 $698M ✓）。确认后全模型统一按该货币跑，报告标注换算汇率 |
| **同链第二个实例：RMB M（FINV 2026-08 实战）** | 信也科技纽交所上市但以**人民币**列报（营收 TTM ¥131.6亿，非 $131.6亿）。检测链同上：`NI ÷ EPS = 股本`（2,383/9.05 = 263M ≈ 当时 ADS 数 253M ✓）；**汇率从公司新闻稿的 US$ 换算反推**（RMB金额÷US$金额，FINV Q2'26 新闻稿 3,259.4/480.4 = 6.78）——**不要凭记忆写死汇率**（2026-06 实际 USDCNY≈6.78，非常见的 7.14）。**收入口径变化陷阱**：监管新规驱动重新分类时，最新新闻稿"净收入"会把历史季重述（FINV Q2'25 从 ¥3,578M 重述至 ¥2,781.3M，-22%）——对比历史必须标注口径，五年序列用 stockanalysis 一致口径 |
| **ADS 比例验证（1 ADS = 8 普通股）** | FUTU：腾讯行情含 "1:8" 字段；电话会纪要 INDUSTRY GLOSSARY 明确 "ADS: representing eight Class A ordinary shares"。验证配方：`NI ÷ EPS = ADS 数` 必须与 `市值 ÷ 价格` 一致。**EPS 永远用 ADS 口径（NI ÷ ADS 数）**，勿混用普通股口径——stockanalysis 的每股数据（EPS/BVPS/股息）都是 ADS 口径，与 ADS 价格直接匹配 |
| **季度页单季净利率骤变 = 事件触发器** | FUTU：Q1'26 净利率骤降至 15.6%（相邻季度 50-56%）→ 顺藤摸瓜发现 CSRC RMB 18.5亿罚款（2026-05-22 宣布）。年度页会把单季异常平滑掉，季度页（`?p=quarterly`）的 Net Income 行 + Profit Margin 行是监管/一次性事件的第一线索。季度净利异常 → 必查当季新闻（罚款/诉讼/减值/一次性收益），再用"剔除非经常项"重算正常化 TTM |

## 2.5 微股本公司 / 保险公司抓取补充（WTM 白山保险 2026-09 实战）

- **腾讯美股市值字段对微股本（<3M 股）公司不可靠**：WTM 股本 2.36M 股、股价 $2,110，腾讯字段[45] 返回 $5.04B 而实际市值 $4.97B（stockanalysis）= 2110.51 × 2.36M——差 ~5%。**微股本高股价公司（WTM/BRK 类）一律用 `stockanalysis` 概览页的 Market Cap ÷ Shares Out 验证，PB 直接用 价格 ÷ BVPS 计算**（BVPS 从公司新闻稿拿，不要依赖 ratios 页）
- **stockanalysis 利润表对保险公司解析为空/行名变体**：保险公司无 "Revenue" 行——行名是分部名（WTM: "Ark/WM Outrigger - Ark"、"Kudu"、"HG Global"），`parse_tables` 正常返回但 key 是分部；总营收在 "Total" 行。季度页（`?p=quarterly`）逐季分部序列是业务动向雷达（分部并表/出表/出售完成都能看到）。解析为空时先打印全部 key，不要断定抓取失败
- **公司官网 IR 403 时抓 prnewswire**：investor.whitemountains.com 对 urllib 返回 403，但 `prnewswire.com/news-releases/...` 同稿可抓（UA 伪装即可）。新闻稿是金矿：CEO 评论（含换帅线索）、分部 CEO 原话（市场/费率判断）、回购股数+价格（资本配置纪律）、未部署资本

## 2.6 费用科目精确口径：SEC XBRL companyconcept API（2026-09 OTA 对比实战）

stockanalysis 四页**不提供费用科目**（营销/研发/销售费用）。要拿精确的「营销费用占营收」做同业对比，走 SEC XBRL：

```python
# 公司 CIK 九位补零；tag 名因公司而异，需试几个
for cik, name in [("0001324424","EXPE"), ("0001075531","BKNG")]:
    for tag in ["SellingAndMarketingExpense","MarketingExpense","SellingGeneralAndAdministrativeExpense"]:
        u = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json"
        req = urllib.request.Request(u, headers={"User-Agent":"research contact@example.com"})  # UA 必填
        d = json.loads(urllib.request.urlopen(req, timeout=25).read())
```
实测：**BKNG 用 `MarketingExpense`**（FY25 $8,186M）、**EXPE 用 `SellingAndMarketingExpense`**（FY25 $7,349M）；tag 不存在时返回 404，静默跳过即可（用 try/except 遍历候选 tag）。同一 filing 会重复出现（10-K 次年带可比期），去重按 `end` 日期取最新。

**同业对比的正确口径**：不要直接比「营销/营收」（两家变现率不同会失真），改比 **营销费用 ÷ 总预订额（Gross Bookings）**——BKNG 4.4 美分 vs EXPE 6.1 美分，这才是获客效率的可比语言。

## 2.7 电话会原文 PDF：公司 IR 的 q4cdn 直链（2026-09 EXPE 实战）

比二手新闻摘要信息量大一个数量级，且可直接 urllib 抓取 + `pdftotext -layout`：
```
https://s202.q4cdn.com/{tenant_id}/files/doc_financials/{YYYY}/q{N}/{TICKER}-USQ_Transcript_{YYYY-MM-DD}.pdf
```
- EXPE 实例：`https://s202.q4cdn.com/757635260/files/doc_financials/2026/q2/EXPE-USQ_Transcript_2026-08-05.pdf`（~50K 字符，含完整经营指标 + 12 位分析师 Q&A）
- 找不到文件名时：先搜 `"{公司} Q{N} {年} earnings call transcript pdf"`，或从 IR 网站 doc_financials 目录模式推；**LSEG StreetEvents 编辑版**为常见来源
- 从原文里能拿到二手报道**永远不会有**的东西：分部 margin 驱动归因、成本削减是否 lapping、CFO 本人陈述（EXPE 案例："I've had an exciting first quarter as part of the Expedia Group team" → 直接暴露 **CFO 换人**，二手新闻只说"appointed new CFO"）、渠道口径（direct mix / AEO / organic 趋势）
- ⚠️ **CFO/CEO 换人信号**：对比相邻两季 transcript 的 CORPORATE PARTICIPANTS 名单，变化即治理事件（EXPE 两年三任 CFO 就是这样发现的）

### 2.8 数据中心重资产公司的 CapEx 双口径与股权重估一次性收益（MSFT 2026-09 实战）

**① 现金流页 CapEx ≠ 真实资本开支（融资租赁表外化）**：数据中心自建商（MSFT/AMZN/GOOGL/META 类）通过融资租赁把部分 capex 移出现金流口径——MSFT FY26 现金口径 CapEx **$116.0B**（stockanalysis 现金流页）vs 公司"全口径指引" **$175B**（含租赁）。两口径差 ~50%，混用让 FCF/NI 差一倍（现金口径 50% vs 全口径 ~15%）。硬规则：
- DCF 的 FCF 起点必须**声明口径**；公司指引"含租赁"时，两口径各给一行
- **OCF 翻倍而 FCF 原地踏步 = capex 吞噬信号**（MSFT FY22→26：OCF 89→183B、FCF 65→67B），比单看 FCF 绝对值信息量大
- ⚠️ **旧报告中标"估"的数字下一轮必须与实际披露核对**——MSFT 2026-08 旧报告写"FY26 FCF ~$20B、FCF/NI 15%、Q4 单季 FCF 转负"，实际 **$67.0B / 50% / Q4 +$19.6B**（旧版混淆租赁口径+季度误记+符号错，三连错都源于拿"全口径 capex 减现金口径 OCF"）

**② 季度净利增速 >> 营业利润增速 = 权益法/公允价值重估一次性收益**（FUTU 罚款案例的反向，收益方向）：MSFT FY26Q2 EPS +59.8% vs 经营利润仅 +21% → 2025-10-28 OpenAI 重组后 27% 股权（~$135B）重估确认 ~+$9B 一次性收益。处理：
- 建**"表面净利 vs 核心净利"双口径**（133.7 vs 124.7B），PE 双标（27.5x vs 29.4x），DCF 用核心口径起步
- stockanalysis ratios 页的 PE/FCF Yield/FCF Yield 全部用污染后 TTM 净利——同业对比前先声明该口径
- 检测触发器：单季 EPS YoY 与营收 YoY 差 >15pct、或单季净利率较相邻季跳升 >3pct → 回查当季权益法/其他收益行

**③ 同业对比循环抓取 + TTM PE 污染信号**：概览页循环（7 个 ticker 一次 urllib 循环 ~35s）拿全市值/PE/FwdPE/52周/营收增速。**TTM PE < FwdPE（成长公司不该出现）= TTM 净利被一次性收益抬高**（GOOGL TTM 17.5x vs Fwd 26.1x）——这类公司在同业表中用 FwdPE 或核心 PE 替代，并加脚注。

## 2.9 财年/TTM 口径陷阱 + 巨型收购后的建模口径（TDG/SNPS 2026-09-30 实战）

**① 财年止 10/11 月的公司：TTM 列 ≠ 当前财年**
- stockanalysis 10Y 页列头为 `TTM | FY2025 | FY2024...`。SNPS（FY 止 10-31）在 2026-09-30 分析时：TTM 止 Jul'26 = FY25Q4+FY26Q1-Q3，而"进行中的 FY2026"没有独立列；TDG（FY 止 9-30）的 TTM 恰好=刚结束的完整财年。**两者含义完全不同，数据包头部必须显式声明 TTM 构成**（如"TTM = FY25Q4+FY26Q1-Q3（止 2026-07-31）"），否则子报告/估值整体错位一年
- ratios 页第一列列头是 "Current"、期末日期为快照日（如 Sep '26）——含义同样是 TTM 快照，不是最新完整 FY
- **腾讯 us 前缀 52 周高低字段不可靠**（SNPS 实测：字段[47] 返回 5.72 垃圾值、[48] 才是 52 周高 539.48）——52 周区间一律以 stockanalysis 概览页 "52-Week Range" 为主源（再用 Markets Insider 等第二源交叉，SNPS 362.55/362.60 ✓）；价格[3]与市值[45]（亿 USD）仍可靠
- **季度现金流页可用**：`cash-flow-statement/?p=quarterly` 给单季 SBC/OCF/FCF/FCF margin + levered/unlevered FCF（balance-sheet 季度页仍为空）

**② 巨型收购并表后 GAAP 全面失真 → 数据包头部"口径总声明"前置**
- SNPS（Ansys $35B，2025-07 交割）：D&A 1,037（营收 11.0%）+ SBC 950（10.1%）把 GAAP 营业利润率砸到 11.0%、GAAP PE 73.6x——**GAAP PE/ROE/ROIC 全部仅存档**；声明唯一口径：估值主锚=调整前瞻 PE（FY26E 指引拼合 EPS），质量锚=OCF/NI（2.73，现金真实性强）+ 含商誉调整 ROIC（SNPS 6.8% < WACC 9% = "为增长付全价"的定量证据；vs TDG 15.6% > WACC = 并购真赚钱——同一指标讲出相反故事，必须双口径并列）
- 负权益公司（TDG 权益 -$9.7B）：ROE/PB 整条禁用，质量锚换 ROA + ROIC 双口径（含商誉 vs 有形对照）
- 通用格式：数据包第 0 节逐条列死（主锚/存档口径/禁用口径），四份子报告禁止另立口径——本季 TDG/SNPS 两轮子代理全部零口径漂移，靠的就是这一节

**③ 巨型收购次年的 DCF 起点规则**
- 收购当年 FCF 被整合成本+利息压低（SNPS FY25 FCF 1,349 vs TTM 2,748）→ **DCF 不从失真年份起步，用正常化 FY N+1 FCF**（指引外推：FY27 营收 × 正常 FCF margin）
- EV 法口径自洽：uFCF = levered FCF + 税后利息（SNPS：2,600 + ~430 ≈ 3,030），终值后 EV→股权 = EV - 净债务
- 四路交叉验证标配：概率加权 DCF（25/50/25）+ 现价隐含 g1（二分法反解）+ 零增长锚（FCF/CoE）+ EPS 路径法（FY27E EPS × 退出倍数贴回）——四数同向才下结论，冲突时写明分歧来源

## 2.10 52/53 周财年公司：指引与建模的双口径（DIS 2026-10 实战）

迪士尼 FY2026（止 2026-10-03）= **53 周财年**。零售/媒体公司每 5-6 年出现一次，是「增速换挡真伪」判断的隐形陷阱：

- **指引双口径必须并读**：DIS FY26E adj EPS $6.71-6.95 → 前瞻 PE 14.7x（含 53 周）/ 15.3x（剔）。额外一周对当年 EPS/营收的抬升约 2-4pp 量级——用含 53 周口径会系统性高估真实增速，直接决定「增速换挡还是继续加速」的结论方向
- **跨年比较（FY26 vs FY25）与 DCF g1 一律用剔除口径**；报告中两个倍数并列标注，与一次性项目剔除同属「口径总声明」第 0 节
- **下一财年反向受压**：FY27 的 YoY 落在 52 周对 53 周的高基数上，FY27 外推同样须声明口径（勿把 FY27 增速放缓误读为基本面恶化）
- **识别信号**：新闻稿/指引注明 "53-week year"、同一指引出现两个增速数字、财年止日期在 10 月初（DIS 止 10-03）且距上次 53 周年约 5-6 年
- 同类公司：零售（WMT/TGT/HD/LOW 等 1 月末止财年）与媒体（DIS 10 月止）均为 52/53 周制——**分析前先核对财年止日期**，stockanalysis 列头不标注 52/53 周差异

## 2.11 REIT 抓取与行情补充（EQIX 2026-10 实战）

- **季度页列序消歧配方**：季度页（`?p=quarterly`）的 Revenue Growth 行是逐季 YoY，**用每一列 ÷ 上年同季列验证列序**（EQIX：2646/2268=+16.67% ✓ → 首列=Q2'26 而非 Q3'26）。二手新闻的季度归属会错（financemagnates 把 Q1'26 报成 $2.44B，实际 $2.47B）——**增速行数学自洽优先于新闻稿转述**
- **52 周低点日期常拿不到**：history 页 HTML 表格行正则抓不到（EQIX 0 rows）、stooq CSV 返回 JS 挑战页、stockanalysis JSON API 403 → 退路：腾讯 52 周高低字段 + wallstreetzen/pandaforecast 等第三方快照，报告中**只写区间不写日期**（"52周区间 $709.79-1,118.60，较高点 -8.3%"），不要猜低点月份
- **⚠️ 个别站点会让整个脚本挂死**：hindenburgresearch.com 类站点 urllib 无响应时，300s script 超时会杀掉**全部已产生输出**。硬规则：`socket.setdefaulttimeout(12)` 全局兜底 + 每次只抓 1 个站点 + 增量 print（不要把多个 fetch 攒到最后一起打印）
- **AFFO 序列重建配方（REIT 专用）**：stockanalysis 四页无 AFFO → 用 Zacks/TradingView 财报快照拼：季值+增速反推上年同季（Q2'26 $11.78 +19% → Q2'25 $9.90），FY 值找 Q4 报道（"FY25 $38.33 +9.5%"），两条路径互验（FY26 指引中值隐含增速 vs 季度加总），对不上的年份标"估"
- **REIT 净杠杆双口径**：公司口径用**年化/run-rate** 调整后 EBITDA（EQIX 3.6x @Q3'25），自算 TTM 口径会给 ~4.0x——capex 高速爬坡期两口径差 0.4-0.5x，报告双列并注明基期

## 2.12 SEC 官方兜底：XBRL 年度序列 + 8-K EX-99.1 新闻稿（UNH 2026-10 实战）

**① stockanalysis 会中途 403，别死磕**：同一会话前半段 200、后半段 403（UA 伪装失效）。兜底走 SEC 官方 XBRL，且 FY 年度序列比聚合站更权威——UNH 实战借此纠正旧报告两处硬伤（FY25 净利实为 $12.06B 而非旧报告 ~$13.3B、OCF $19.7B 而非 ~$28B）：

```python
# CIK 九位补零（UNH=0000731766）；UA 必填（sec.gov 规则，带联系方式）
tags = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
        "NetIncomeLoss", "NetCashProvidedByUsedInOperatingActivities", "EarningsPerShareDiluted"]
for tag in tags:
    u = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json"
    d = json.loads(urllib.request.urlopen(urllib.request.Request(
        u, headers={"User-Agent": "research contact@example.com"}), timeout=25).read())
    for e in d["units"]["USD"]:
        if e.get("form") == "10-K" and e.get("fp") == "FY" and (e.get("frame") or "").startswith("CY"):
            ...  # 每个日历年一条；NetIncomeLoss = 归母口径
```
- tag 404 静默跳过（§2.6 同款）；同 period 重复出现（10-K 次年带可比期）按 `end` 取最新
- **季度概念多数无 frame**（如 StockholdersEquity 季度值）→ 改按 `end` 日期过滤，勿依赖 frame
- **倍数计算的 $M/$B 混用陷阱（§2 单位陷阱的倍数版）**：报表值 $M、模型假设 $B 混用时倍数虚高 1000 倍（UNH：P/B 36.0x / EV/EBIT 148.6x → 统一 $M 后 3.60x / 16.5x）。倍数合理性自检：成熟公司 PB 1-5x、EV/EBIT 8-25x、FCF yield 3-10%

**② 8-K EX-99.1 新闻稿 = 指引演化/分部/会员表的一手来源**（替代"web_search 拼新闻"）：
```
data.sec.gov/submissions/CIK{cik}.json    # recent[] 取 form=='8-K' 且 date≈财报日
→ https://www.sec.gov/Archives/edgar/data/{cik}/{acc去横线}/index.json
→ 找 earningsrelease*.htm（EX-99.1）→ 去 HTML 标签 → 正则抓 outlook/指引表
```
UNH 实战：Q3'26 8-K（2026-10-13）一次拿全——单季营收 $112.7B / 调整后 EPS $4.69 / MCR 88.4% / 分部 EFO / 会员数 / 债务资本比 / **指引演化表（prior vs current 两列对照）**。硬规则：**"指引上调/下调"类断言必须引用新闻稿演化表，禁止新闻转述**。

## 3. 兜底路径

- 指引/事件/分部细节：web_search（如 `"Netflix" guidance revenue operating margin 2026`、`"NFLX" stock drop reason 日期`）
- 实时行情：腾讯 API us 前缀（字段表见 `hk-stock-data-sources.md` 第 5 节）
- akshare `stock_financial_hk_analysis_indicator_em` 只覆盖港股，美股不适用
