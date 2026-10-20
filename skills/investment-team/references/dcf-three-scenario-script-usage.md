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
