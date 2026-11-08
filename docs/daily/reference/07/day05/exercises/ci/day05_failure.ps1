$ErrorActionPreference = 'Stop'
$lessonBranch = git branch --show-current
if ($lessonBranch -notlike 'codex/ci-practice*') { throw '仅在自己的练习分支做此实验' }
git add -- tests/test_ci_probe.py
git commit -m 'Demonstrate CI assertion failure'
if ($LASTEXITCODE -ne 0) { throw '故意失败提交未完成' }
git push origin HEAD
if ($LASTEXITCODE -ne 0) { throw '推送失败' }
Write-Output '等失败run结束，下载artifact，找到probe断言后，再执行下面的恢复步骤。'
