# dcf_three_scenario.py 程序化调用须知（2026-10 东鹏重析实战）

跑三情景 DCF / 反向 DCF 时在 execute_code 里直接 import `scripts/dcf_three_scenario.py`。三个机械层坑（边界命中"只报边界不引用边界值"的报告纪律见 `reverse-dcf-analysis.md` 与常见陷阱表，此处不重复）：

## 1. import 即执行内置 demo

脚本 import 时会先跑一段内置演示（打印另一家公司的完整估值输出）。程序化调用必须抑制 stdout：

```python
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    sys.path.insert(0, "<skill_dir>/scripts")
    from dcf_three_scenario import (
        _dcf_value, implied_g1, implied_tg, implied_irr,
        implied_sustainable_fcf, zero_growth_anchor, price_vs_scenarios)
```

## 2. 反向 DCF 函数返回 dict，不是 float

| 函数 | 返回 |
|---|---|
| `implied_g1` / `implied_tg` / `implied_irr` | `{"hit_boundary": bool, "side": "above"/"below"/None, "range": (lo, hi), "g1"/"tg"/"irr": value 或 None}` |
| `implied_sustainable_fcf` | float（EV 法：`ev*(wacc-tg)/(1+tg)`） |
| `zero_growth_anchor` | `{"iv_zero": 总额, "per_share": 每股, "sensitivity": {wacc: iv}}` |

直接 `f"{result:.1%}"` 会抛 `TypeError: unsupported format string passed to dict.__format__`——先取键再用。命中边界时 value 为 None，按规范只报"命中{side}边界、测试范围 {range}"。

## 3. 敏感性矩阵不必走高层函数

WACC×tg 矩阵直接调 `_dcf_value(g1, wacc, tg, fcf0)` 得企业价值，`(EV + 净现金) / 股本` 得每股 IV。

## 已验证调用骨架（东鹏 2026-10，可复制改参）

```python
PRICE, SHARES = 109.45, 7.342          # 亿股
FCF0, NETCASH  = 40.0, 156.5           # 正常化FCF / 净现金（亿）
scenarios = {
    "悲观": dict(g1=0.00, g2=0.00, tg=0.010, wacc=0.095),
    "基准": dict(g1=0.10, g2=0.04, tg=0.025, wacc=0.090),
    "乐观": dict(g1=0.16, g2=0.06, tg=0.030, wacc=0.085)}
for name, s in scenarios.items():
    ev = _dcf_value(s["g1"], s["wacc"], s["tg"], FCF0)
    iv_ps = (ev + NETCASH) / SHARES          # 三情景每股 IV
g1r = implied_g1(PRICE, SHARES, FCF0, 0.09, tg=0.025)   # dict，取 ["g1"]
anchor = zero_growth_anchor(FCF0, 0.09, NETCASH, SHARES,
                            wacc_range=(0.085, 0.10))     # dict，取 ["per_share"]
rows, verdict = price_vs_scenarios(PRICE, {"悲观":81.6, "基准":172.8,
                                           "乐观":300.5, "零增长锚":81.9})
```

注意脚本原生 `_dcf_value` 的显性期为 10 年单段 g1（无 g2 分段）——g2 只在上面的自算骨架里体现（5年g1+5年g2 结构用两次 _dcf_value 拼或自行折现）。

## 4. 重析轮公式复现：先扫「公式形状」再调参数（2026-10-31 归创通桥 2190.HK 实战）

SKILL.md ⑤ 参数复现法默认在脚本公式形状上调参，但**首轮报告的 DCF 公式可能与脚本默认不同形**——归创首轮实为「5 年显性 g1（逐年衰减）+ Gordon TV」，而脚本默认 10 年单段，参数怎么调都对不上首轮 IV。正确姿势是**变体扫描**：

```python
variants = ["10年常数g1",   # 脚本 _dcf_value 默认
            "5年显性+GordonTV",  # 归创首轮实际形状
            "线性衰减", "两段g1+g2"]
# 对拍首轮三情景 IV（归创首轮 24.6/27.6/31.0 HKD），全情景误差 <0.02 RMB/股 → 形状+参数双锁定
```

锁定后只替换输入值（净现金/FCF0/股本）重跑，IV 的同比变化即可干净归因（归创轮：同口径 IV 下移 1.1 全为净现金消耗，生意假设零变化）。

## 5. implied_g1 无净现金参数——净现金大户必须调价后求解

脚本签名 `implied_g1(price, shares, fcf0, wacc, tg)` 把市价×股本整体当 EV（无净现金扣减参数），而 `zero_growth_anchor` 天然含净现金。净现金占市值 30%+ 的公司（归创 40%）若不调整，隐含增速会把净现金误归经营能力、系统性偏高，且与含净现金的三情景 IV / 零增长锚口径不可比。修正：`price_adj = price − 净现金/股本` 后再传给 implied_g1，报告中注明「生意口径（剔净现金）」；两口径并列时各自标注，不得混用落点判读。
