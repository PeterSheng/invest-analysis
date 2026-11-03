# 全局建模参数修改配方（skill 自身的标准变更流程）

> 适用触发：用户要求统一或修改全局建模参数——折现率（WACC）、永续增长率（tg）、评分权重、星级精度、模板默认值等跨多文件的框架级参数。

## 五步流程（2026-11-03 统一 WACC=10%/tg=3% 实战验证：10 处替换一次全过、全程 ~1 分钟）

### 第 1 步：口径盘点（区分「处方」vs「历史叙述」）
grep 扫描整个 skill 目录（SKILL.md + references/ + templates/ + scripts/）找参数所有出现：
- **处方性出现（必须改）**：模板默认值与注释、示例调用骨架中的参数行、敏感性矩阵推荐区间、校准建议句（如"必须手动校准 tg=2.5-3%"）
- **历史案例叙述（保留原值）**：实战报告里按当时口径算出的 IV/评分/敏感性数字——**不重写已交付的历史数字**，改法是"保留原值 + 标注历史口径存档 + 指向新规范"（WM 6.5-8%、MTD 7.5-9.5%、REIT 8% 均如此处理）。repo `reports/` 里的历史报告正文一律不动。

### 第 2 步：先重算演示值，再改文档
文档中内嵌输出数字的代码骨架/示例（如 `dcf-three-scenario-script-usage.md` 东鹏骨架的 IV 81.6/172.8/300.5、零增长锚 81.9）在参数变更后**全部失真**——失真的文档数字比缺失更危险（未来会话会直接引用）。先 import 脚本用新参数实跑一遍，把新数字准备好再动手改文档。

### 第 3 步：批量原子替换（execute_code 单脚本）
全部 old/new 对写进一个脚本，每处断言 `text.count(old) == 1`：1=替换、0 且 new 已在文中=幂等跳过、其他=PROBE 不动文件，逐条回显命中状态。**不逐处 patch**——长中文行 + 行号描述直接 patch 的 old_string 猜不准（同审计批量修复配方）。先跑一遍纯计数探查（不写盘）确认全部命中后再真正替换，避免半套替换。

### 第 4 步：三重验证
1. **语法**：修改过的 .py 全部过 `py_compile`
2. **实跑对拍**：文档中的代码骨架原样实跑，输出必须与新写入文档的数字逐一吻合（本次 85.7/156.0/231.5/75.8 全对上）
3. **残留扫描**：grep 旧口径处方（旧区间/旧默认值如 `tg=2.5-3`、`wacc = 0.08`），确认剩余命中全部是历史叙述

### 第 5 步：镜像 + 推送
copytree 真镜像（`dirs_exist_ok=True` + 删除源中已不存在文件，跳过 `__pycache__`/`.git`）→ `git add skills/investment-team` → commit message 列明改动文件与重算值 → fetch-first 自动 `git pull --rebase` 重试推送（模板 `templates/git-push-report.py`，subprocess 用 list 参数传 commit message，勿手搓 shell 字符串插值）。镜像 diff 里出现往轮遗留未同步文件时顺带补齐（本次带出了 ah-dual-listing-analysis.md）。

## 实战记录
- **2026-11-03**：统一 WACC=10% / tg=3%（commit cec33c8）。10 处替换（SKILL.md×4、`templates/financial-model-template.py`×1、`references/reverse-dcf-analysis.md`×2、`references/reit-analysis-guide.md`×1、`references/negative-equity-buyback-machine-analysis.md`×1、usage 骨架整段重写×1）全 OK；东鹏骨架按统一口径重算 85.7/156.0/231.5/75.8 实跑吻合；镜像 63 文件含 1 个往轮遗留。
