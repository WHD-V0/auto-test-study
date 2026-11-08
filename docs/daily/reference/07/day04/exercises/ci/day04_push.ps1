$ErrorActionPreference = 'Stop'
git remote get-url origin
if ($LASTEXITCODE -ne 0) { throw '先配置你自己的origin仓库' }
$lessonBranch = git branch --show-current
if ($lessonBranch -notlike 'codex/ci-practice*') { throw '先切换到自己的codex/ci-practice练习分支' }
git status --short
git diff --check
if ($LASTEXITCODE -ne 0) { throw '先修复差异格式问题' }
.\.venv\Scripts\python.exe -m pytest
if ($LASTEXITCODE -ne 0) { throw '本地回归未通过' }
# 先由本人检查并提交具体练习文件，再运行推送；不自动git add整个仓库。
git push -u origin HEAD
if ($LASTEXITCODE -ne 0) { throw '推送失败，保留Git输出' }
Write-Output '到自己的GitHub Actions查看该提交，等两个OS完成并下载artifact。'
