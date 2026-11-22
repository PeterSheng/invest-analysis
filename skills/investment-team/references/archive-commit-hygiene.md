# 归档与提交操作细则（Archive & Commit Hygiene）

配合 SKILL.md「归档铁律」使用。规则是"必须落盘当月、绝不改历史"；本文是**怎么执行**，含已踩过的坑。

## §1 写盘前（3 步）
1. `os.path.exists("/home/admin/hermes-agent-invest/reports/{YYYYMM}")` — 当月目录常已存在（同月其他公司分析），**不要**假设需要新建，也不要因"已存在"就复用旧目录名。
2. 台账查重：读 `references/analyzed-companies-ledger.md`，确认该公司在本月/历史是否有记录。首轮 → `{TICKER}`；同月重析 → `{TICKER}-重析`；第二轮 → `{TICKER}-v2`。绝不覆盖。
3. 分析日 = 运行当天日期，不是财报期末、不是价格日。价格日只在数据包 §一 标注"价格截至"。

## §2 文件与目录固定结构
```
reports/{YYYYMM}/{TICKER}/
  00-数据包.md            ← 唯一数据源，先落盘；四份子报告必须 read_file 它
  01-商业模式-段永平视角.md
  02-财务估值-巴菲特视角.md
  03-风险分析-芒格视角.md
  04-长期趋势-李录视角.md
  05-综合裁决.md
```
子报告（delegate_task 派发）一律要求：先读 00-数据包全文、引用其 §五 估值，不自行重算 EPS/IV —— 同一家公司在四份报告里不能有四个 EPS。子报告最后一行为四维等权评分（1–5 分，精确到 0.25），05 用四条子报告分做等权平均，必须能在最后一行精确复算（如 14.10/4 = 3.525 → 3.53）。

## §3 提交（scoped add，禁止 git add -A）
仓库 `~/hermes-agent-invest`，remote `git@github.com:PeterSheng/invest-analysis.git`。
```
git add reports/{YYYYMM}/{TICKER} skills/investment-team/references/analyzed-companies-ledger.md
git status --porcelain      # 确认只有本轮文件；有无关脏文件就停下排查
```
禁止 `git add -A` / `-a`：仓库里常有 skill 镜像同步产生的文件与其他未完成改动，全量 add 会把别人的轮次混进本次 commit，破坏"一个 commit 只含本轮新增"的可审计性。

## §4 commit message 含 `$` 价格 —— 必须用 -F 文件
**已踩坑（TJX 首轮，commit 需 amend 修复）**：
```python
subprocess.run("git commit -m 'TJX ... 收盘 $131.09，IV $91.9，击球区 $95-110'", shell=True, ...)
# 实际 message 变成：31.09 / 1.9 / 5-110
```
原因：shell=True + 命令字符串在构造时若经过双引号/模板插值，`$131.09` 被当作变量 `$1` + "31.09" 展开，`$95` 被当作位置变量。单引号只有在**字符串真的被 shell 原样解析**时才安全，构造路径一多就不可靠。

正确做法：
```python
msg = "TJX 四大师首轮分析（2026-11-17，收盘 $131.09）：综合 3.53，基准 IV $91.9（-30%），击球区 $95-110"
open("/tmp/commitmsg.txt","w").write(msg)
subprocess.run(["git","commit","-F","/tmp/commitmsg.txt"], cwd=repo)   # 不用 shell，用 list
```
要点：**参数列表 + shell=False + -F 文件**，价格符号零风险。

## §5 提交后验证与补救
```
git log --oneline -1          # 逐字核对标题里的 $ 数字是否还在
git show --stat --oneline HEAD | head -15   # 确认只包含本轮文件
git push origin main
```
若 message 已失真：`git commit --amend -F /tmp/commitmsg.txt` → `git push --force-with-lease origin main`。单用户仓库可 amend，**永远不用裸 `--force`**；amend 只改标题，绝不顺带 `git add` 新文件（那会把内容混入同一 commit）。

## §6 台账登记
在 `references/analyzed-companies-ledger.md` 的**当月小节**末尾追加（不新建章节）：四大师分、综合分、价格与价格日、距 52 周高/低、YTD、本轮口径审计要点、一次性项、证伪线、报告路径。同一月份只保留一个小节，避免台账分裂。

## §7 事件驱动重估
报告内若标注了"下一次财报日期"，该日期触发时必须**新建 `{TICKER}-重析` 目录**（同月）重跑，并在新数据包 §一 写"价格截至"重拉价 —— 禁止回写本轮文件、禁止沿用旧价（DVA 教训：$239.88 旧价 vs 实际 $188.69）。
