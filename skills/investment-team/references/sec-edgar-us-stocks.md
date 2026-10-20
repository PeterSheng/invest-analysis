# SEC EDGAR 美股数据提取指南

## 基础用法

### 1. 查找公司CIK

```bash
# 方法A：直接搜索
curl -s "https://www.sec.gov/cgi-bin/browse-edgar?CIK=ROL&action=getcompany"

# 方法B：已知常见CIK
# ROL=0000084839, AAPL=0000320193, BRK=0001067983, KO=0000021344
```

### 2. 获取财务数据（单次少量字段，防超时）

```bash
CIK=0000084839  # Rollins

curl -sL -H "User-Agent: Mozilla/5.0 (admin@example.com)" \
  "https://data.sec.gov/api/xbrl/companyfacts/CIK${CIK}.json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
usgaap = data['facts']['us-gaap']

# 只取需要的字段，每次请求控制在8个以内避免超时
metrics = {
    'Revenue': 'Revenues',
    'NetIncome': 'NetIncomeLoss',
    'OpIncome': 'OperatingIncomeLoss',
    'OpCF': 'NetCashProvidedByUsedInOperatingActivities',
    'CapEx': 'PaymentsToAcquirePropertyPlantAndEquipment',
    'Assets': 'Assets',
    'Equity': 'StockholdersEquity',
    'LT_Debt': 'LongTermDebt',
    'Shares': 'CommonStockSharesOutstanding',
    'EPS': 'EarningsPerShareDiluted',
    'Dividends': 'PaymentsOfDividendsCommonStock',
    'GrossProfit': 'GrossProfit',
}

for label, key in metrics.items():
    units = usgaap.get(key,{}).get('units',{}).get('USD',[]) or \
            usgaap.get(key,{}).get('units',{}).get('shares',[])
    # 去重：同FY取最近filed的10-K
    k10s = {}
    for r in units:
        fy = r.get('fy')
        form = r.get('form','')
        if fy and form.startswith('10-K'):
            filed = r.get('filed','')
            if fy not in k10s or filed > k10s[fy][1]:
                k10s[fy] = (r.get('val'), filed)
    vals = [f'FY{fy}:{val/1e6:.0f}M' for fy, (val,_) in sorted(k10s.items())[-5:]]
    if vals:
        print(f'{label}: {\" | \".join(vals)}')
"
```

### 3. 关键注意事项

- **去重是必须的**：同一FY年份可能有原始10-K + 10-K/A修正稿，取filed日期最新的
- **超时处理**：整个companyfacts JSON可能10MB+，请求全部字段会超时（>15s）。分成2-3次请求，每次8个字段以内
- **单位处理**：大部分字段是USD，Shares字段是shares单位，EPS已经是每股数据
- **⚠️ EPS单位陷阱**：`EarningsPerShareDiluted` 使用 `USD/shares` 作为 units 键名（非 `USD`）。脚本中 `units.get('USD',[])` 对 EPS 返回空。正确写法是遍历 `units` 的所有键：`for unit_key in units: for v in units[unit_key]: ...`
- **Quarterly数据**：form='10-Q'是季报，用form='10-K'过滤只取年报
- **货币**：美股默认USD，中概股可能有CNY字段 — 查看units的key确认

### 4. 已知CIK速查

| 公司 | Ticker | CIK |
|------|--------|-----|
| Rollins | ROL | 0000084839 |
| Copart | CPRT | 0000900075 |
| AutoZone | AZO | 0000866787 |
| O'Reilly | ORLY | 0000898173 |
| Fastenal | FAST | 0000815556 |
| Cintas | CTAS | 0000723254 |
| Old Dominion | ODFL | 0000878927 |
| Pool Corp | POOL | 0000932841 |
| Zoetis | ZTS | 0001555280 |
| Intuit | INTU | 0000896878 |
| Waste Management | WM | 0000823768 |

| 查询新公司CIK：`https://www.sec.gov/cgi-bin/browse-edgar?CIK={TICKER}`

## 5. 解析脚本模板（健壮版）

以下模板处理了EPS的`USD/shares`单位问题，并正确去重10-K修正稿：

```python
import urllib.request, json

CIK_PADDED = '0001286681'  # DPZ
url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK_PADDED}.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (admin@hermes-agent.com)', 'Host': 'data.sec.gov'})
data = json.loads(urllib.request.urlopen(req, timeout=30))
us_gaap = data['facts']['us-gaap']

def get_10k(concept):
    """遍历所有unit keys获取10-K值，按FY去重取最新filed"""
    if concept not in us_gaap: return {}
    result = {}
    for unit_key in us_gaap[concept]['units']:  # 不假设key为'USD'
        for v in us_gaap[concept]['units'][unit_key]:
            if v.get('form') == '10-K' and v.get('fp') == 'FY':
                fy = v.get('fy')
                if fy not in result:  # 第一个遇到即最新(已排序)
                    result[fy] = v.get('val')
    return result
```

## 6. ⚠️ 10-K 值去重陷阱与季度交叉验证（2026-08 WM/TEM 双重实战）

**"按 FY 取最新 filed 去重"的逻辑在部分公司会产出错位一年的数据。** 实战证据：

| 公司 | 现象 | 根因 |
|------|------|------|
| WM（0000823768） | `RevenueFromContractWithCustomerExcludingAssessedTax` 的 FY2025 有 **3 个不同值**（$20.43B / $22.06B / $25.20B），分别对应 FY2023/FY2024/FY2025 的真实数据；按"最新 filed"去重后 FY2025 只剩 $20.43B——**收入序列整体错位一年** | SEC 的 `fy` 标签基于 filing 上下文而非报告期，概念首次启用/重述时同一 fy 会挂多个报告期的值 |
| TEM（0001717115） | 10-K 的 `NetIncomeLoss` FY2024=-$290M 但 9M'24 累计已达 -$693M（不可能）；`StockholdersEquity` 10-K 报 -$1,129M 而 10-Q 报 +$491M；`RevContract` FY2024=$321M 而新闻披露全年 $693M | IPO 后公司（优先股转换、收入重述、可赎回工具分类）的 10-K 口径与 10-Q 系统性不一致 |

**正确的数据验证配方（写入报告前必做）：**

1. **先看原始值数组，不做严格去重**——若同一 fy 出现多个不同 val（WM 案例），说明 fy 标签错位，取**最大/最接近共识**的值，或用 10-Q 重建。
2. **用 10-Q 季度累计数据重建年度**：`FY = Q4累计`、`Q2单季 = H1累计 - Q1累计`。WM 验证：10-Q 重建的 Q2'26 单季 $6,684M 与财报新闻（TradingView）逐项吻合 ✓；而 10-K 的 RevContract 是错的。
3. **与财报新闻披露数字对拍**：营收/净利/EPS 至少与一个权威新闻源（GenomeWeb/TipRanks/公司新闻稿）核对。TEM 的 FY2024 $693M / FY2025 $1.27B 来自新闻而非 companyfacts。
4. **资产负债表以最新 10-Q 为准**（TEM：权益 10-K 报负、10-Q 报正，属可赎回工具分类差异，写报告用 10-Q 口径并注明）。
5. **季度序列的 `end` 键天然按报告期去重**（get_q 用 end 去重无此问题），10-Q 数据比 10-K 可靠。

> 教训：SEC companyfacts 是**权威原始库但不是权威口径库**——先交叉验证再建模，宁可多花 5 分钟对拍，不要写完报告再改（沿用 SKILL.md 第 1.5 步原则）。
```

## 6. WM 实战陷阱（2026-08）：多值概念去重、CapEx 概念切换、Q4 累计值位置

对 WM（CIK 0000823768）拉 companyfacts 时发现三类通用性强的坑：

### 6.1 同一 fy 出现多个 10-K 值——盲目去重会选错年份

`RevenueFromContractWithCustomerExcludingAssessedTax` 返回 4 条：`(2024, 22063M), (2025, 20426M), (2025, 22063M), (2025, 25204M)`——三条都标 fy=2025，实际对应 FY2023/FY2024/FY2025。按"取最新 filed"去重会错选 $20.43B（实为 FY2023 营收）当 FY2025，导致全年增速、净利率全部错位。

**正确姿势**：① 去重前先把该 concept 的 10-K 全量值打印出来人工核对；② 用 10-Q 累计序列交叉验证——FY 值必须 ≥ 9M 累计值（FY2025=$25.2B > 9M'25=$18.9B ✓；而 $20.43B < $18.9B 明显是错配）；③ 与新闻/聚合器披露的全年数对拍。

### 6.2 CapEx 概念会切换

`PaymentsToAcquirePropertyPlantAndEquipment` 在 FY2022 后停止上报，WM 改用 `PaymentsToAcquireProductiveAssets`（含 PP&E + 其他生产性资产采购，口径更宽）。**拉 CapEx 必须同时查两个 concept，选有值且连续的那个**（WM：2021 $1.82B / 2022 $1.63B / 2023 $1.90B / 2024 $2.59B / 2025 $2.90B 用 ProductiveAssets）。

### 6.3 Q4 累计值在 10-K 里，不在 10-Q 里

`form='10-Q'` 过滤拿不到 12-31 的年度累计值（它在 10-K 中）。**用季度序列重建年度**：FY = 10-K 全年值（即 Q4 累计），单季 = 相邻累计值相减（Q2'26 = 12911 − 6227 = $6,684M，与 TradingView 新闻披露 $6.684B 逐项吻合 ✓——这是最可靠的交叉验证法）。

### 6.4 搜索结果里的 SEC 链接可能不是目标公司

搜索 "Waste Management 2024 annual" 返回 `exhibit99tofebruary52025.htm`（CIK 37996）声称"2024 营收 $18.5B 净利 $5.9B"——**那不是 WM**（WM CIK 是 0000823768）。用任何 SEC 链接数据前先验证 CIK 与公司名匹配，再与 companyfacts 对拍。
