# IPO 分析与打新专项指南

> 当用户要求分析一家即将/正在 IPO 的公司，且明确问及「打新」「申购」「是否值得参与」时，激活本参考。

---

## 一、与常规上市公司分析的关键差异

| 维度 | 常规分析 | IPO 分析 |
|:---|:---|:---|
| 数据来源 | 季报/年报/QSR 财报 | **S-1 注册声明**、路演材料、招股书摘要 |
| 价格 | 实时市场定价 | **定价区间**（$X-$Y），最终定价在上市日确定 |
| 估值分析 | 单一价格下的 PE/PB/DCF | **区间敏感性分析**：低端、中位、高端分别计算 |
| 股权结构 | 相对稳定 | **锁定+退出结构**是核心：Primary vs Secondary 比例 |
| 决策输出 | 买入/持有/卖出 | **打新策略**：参与/观望/短线博弈/不参与 |
| 核心风险 | 商业模式/竞争/估值 | 额外叠加：**PE 套现动机、锁定期抛压、首日情绪溢价** |

---

## 二、IPO 数据搜集清单（S-1 专项）

在常规数据搜集（见 `references/data-collection-pattern.md`）基础上，追加以下 IPO 专项查询：

### Round A: IPO 结构（与常规数据同步第一轮）
```
"{公司名} IPO price range shares outstanding valuation {年份}"
"{公司名} S-1 filing revenue net income EBITDA {年份}"
"{公司名} IPO underwriters bookrunners NYSE NASDAQ ticker"
```

### Round B: 深度挖掘
```
"{公司名} S-1 primary secondary shares selling shareholders"
"{公司名} IPO use of proceeds debt paydown"
"{公司名} lock-up period expiration date"
"{公司名} founder CEO ownership post-IPO stake"
```

### Round C: 同行对标
```
"{公司名} IPO valuation comparison {可比公司1} {可比公司2} PE multiple"
"{行业} IPO 2026 recent debuts performance"
```

### 关键数据提取清单

| 数据点 | S-1 常见位置 | 重要性 |
|:---|:---|:---:|
| Primary vs Secondary 比例 | Use of Proceeds / Underwriting | 🔴 必查 — 68%+ secondary = PE 退出 |
| 净募资用途 | Use of Proceeds | 🔴 必查 — 还债 vs 扩张，性质不同 |
| 总债务 | Capitalization table | 🔴 必查 — LBO 遗留债务是关键风险 |
| 锁定期（Lock-up） | Underwriting → Lock-Up | 🟡 重要 — 180天是标配 |
| Post-IPO 实控人持股 | Principal Stockholders | 🟡 重要 — PE 剩余持股比例 |
| 历史股东回报 | 通常不在 S-1 中 | 🟢 参考 — Blackstone $8B 收购价 vs IPO 估值 |

---

## 三、IPO 估值建模调整

### 3.1 多点价格建模（必须）

IPO 分析**必须**在三个价格点分别计算估值：

```python
for ipo_price in [low, mid, high]:
    mkt_cap = ipo_price * shares_post_ipo
    pe = ipo_price / eps
    ps = mkt_cap / revenue
    ev = mkt_cap + debt - cash
    # ... 全部估值指标
```

### 3.2 LBO 后遗症检查

PE 收购后快速上市的公司，必须检查：

| 检查项 | 判断标准 | JMKE 案例 |
|:---|:---|:---|
| 收购到 IPO 时间 | <3 年 = 包装上市 | 18 个月 ⚠️ |
| 债务/NI 比率 | >10x = 危险杠杆 | 38x 🔴 |
| 利息覆盖率 | <3x = 脆弱 | ~2.1x 🔴 |
| EV vs 收购成本 | 显著高于收购价 = PE 赚差价 | 基本持平（急于退出） |

### 3.3 加盟模型特别关注

如果目标公司是加盟模型（如餐饮连锁）：

- **不要混淆 systemwide sales 和 franchisor revenue** — S-1 中 royaly 收入才是公司的真实收入
- **Royalty rate 可持续性** — >10% 的 royalty rate 在行业中是偏高的，长期不可持续
- **AUV vs royalty rate 的张力** — 加盟商利润 = AUV × (1 - COGS% - labor% - royalty%)，如果 royalty 太高，加盟商 ROI 被压缩

---

## 四、打新决策框架

### 4.1 三类打新场景

| 类型 | 定义 | 适合条件 | JMKE 案例 |
|:---|:---|:---|:---|
| **基本面打新** | 估值合理 + 长期成长 + 好生意 | PE < 同行中位数 | ❌ PE 133x |
| **情绪打新** | 稀缺性溢价 + 首日涨幅博弈 | 行业热度 + 品牌知名度 | ⚠️ 餐饮 IPO 稀缺 |
| **安全边际打新** | 破发也敢持有 | 低杠杆 + 健康现金流 | ❌ $2.1B 债务 |

### 4.2 打新决策输出格式

综合报告中必须包含以下结构：

```
## IPO 打新专项分析

### 1. IPO 性质判断：「PE 退出型」vs「增长融资型」
### 2. 定价合理性分析（PE/PB/PS/EV 对标）
### 3. 首日表现历史参照（3-5 个可比 IPO）
### 4. 打新决策矩阵（A/B/C 三种策略 + 适合人群）
### 5. 综合打新建议（明确：参与/不参与/观望）
```

### 4.3 决策矩阵模板

| 策略 | 适用投资者 | 操作 |
|:---|:---|:---|
| 🚫 不参与 | 价值投资者、长期持有者 | 估值无安全边际 |
| ⚠️ 短线博弈 | 有经验、愿承担破发风险 | 设首日止损线 |
| ✅ 观望 | 大部分投资者 | 等锁定期抛压释放后评估 |

### 4.4 后续观察时间表

报告中应给出追踪节点：

| 时间 | 事件 | 关注点 |
|:---|:---|:---|
| IPO 首日 | 上市交易 | 涨跌幅、成交量 |
| +90 天 | 首个完整季报 | 首份公开季报的同店增速 |
| +180 天 | 锁定期到期 | PE/老股东是否减持 |
| +365 天 | IPO 一周年 | 估值是否回归合理区间 |

---

## 五、与现有流程的集成方式

### 报告结构调整

IPO 分析时，综合报告调整为：

```
{公司名}-四大师综合报告.md
├── 一、公司速览（含 IPO 定价信息表 + S-1 关键数据）
├── 二、四大师评分汇总
├── 三、各大师核心判断
├── 四、IPO 打新专项分析 ← 新增核心章节
│   ├── IPO 性质判断
│   ├── 定价合理性分析
│   ├── 首日表现历史参照
│   ├── 打新决策矩阵
│   └── 综合打新建议
├── 五、AlphaFind 终极一问
└── 六、后续观察点（含锁定期时间表）
```

### 不需要单独创建 05-IPO专项分析.md

因为 IPO 是本次分析的核心，不是「附加事件」。将其作为综合报告的第四章节即可。只有当用户已经做过常规分析、后来又追加询问 IPO 时，才创建独立的 `05-IPO专项分析.md`。

---

## 六、常见陷阱

| ❌ 陷阱 | ✅ 正确做法 |
|:---|:---|
| 用 systemwide sales 代替 franchisor revenue 建模 | 加盟公司的真实收入是 royalty + 加盟费，不是 systemwide |
| 忽略 Primary/Secondary 比例 | IPO 中 68%+ 来自老股东 = PE 退出信号，必须在报告中分析 |
| 只用 DCF 一种估值方法 | 加盟模型用「终值倍数法」（25x FCF 终值）补充 DCF |
| 忽略 LBO 遗留债务 | PE 收购后的债务是 IPO 后压在公众股东头上的负担 |
| 只用单一价格点做估值 | IPO 必须做低/中/高三档价格敏感分析 |
| 把打新建议写成买/卖二元结论 | 给出多策略矩阵（不参与/短线博弈/观望）+ 各策略适合人群 |
