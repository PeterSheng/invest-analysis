"""四大师报告 GitHub 推送模板（SKILL.md 第五步：推送是强制的，不可跳过）。

用法：复制进 execute_code，修改 report_dir 与 commit_msg 后运行。
含：git 身份设置、add/commit/push、push rejected "fetch first" 时自动
git pull --rebase 后重试（远程常有其他会话推的新提交，盲目重试无效）、
commit hash 回显。推送后必须向用户报告 commit hash。
"""
import subprocess, sys

repo = "/home/admin/hermes-agent-invest"
report_dir = "reports/YYYYMM/公司名/"  # 替换为实际路径

# 1. 确保 git 身份
subprocess.run(["git", "-C", repo, "config", "user.name", "PeterSheng"], capture_output=True)
subprocess.run(["git", "-C", repo, "config", "user.email", "zjsxssj@gmail.com"], capture_output=True)

# 2. 暂存
r = subprocess.run(["git", "-C", repo, "add", report_dir], capture_output=True, text=True)
print("git add:", "OK" if r.returncode == 0 else f"FAIL: {r.stderr}")

# 3. 提交
commit_msg = "add: {公司名} 四大师综合分析 — 综合评分 {分数}/5"
r = subprocess.run(["git", "-C", repo, "commit", "-m", commit_msg], capture_output=True, text=True)
print("git commit:", r.stdout.strip() or "OK")

# 4. 推送（失败先 pull --rebase 再重试——远程常有其他会话推的新提交）
for attempt in range(2):
    r = subprocess.run(["git", "-C", repo, "push", "origin", "main"], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        break
    if "fetch first" in (r.stderr or ""):
        subprocess.run(["git", "-C", repo, "pull", "--rebase", "origin", "main"], capture_output=True, text=True, timeout=30)
    print(f"Push attempt {attempt+1} failed, retrying...")

if r.returncode != 0:
    print(f"❌ PUSH FAILED after 2 attempts: {r.stderr}")
    sys.exit(1)

# 5. 获取 commit hash 确认
r2 = subprocess.run(["git", "-C", repo, "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
print(f"✅ Pushed to GitHub: commit {r2.stdout.strip()}")
