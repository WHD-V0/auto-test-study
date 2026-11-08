$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force reports/learning/archive | Out-Null
.\.venv\Scripts\python.exe -m pytest -n 2 --html=reports/learning/archive/report.html --self-contained-html --junitxml=reports/learning/archive/junit.xml
if ($LASTEXITCODE -ne 0) { throw '归档完整并行回归失败' }
Write-Output '本地通过；还需在相同代码版本的Linux和自己的远程CI验证。'
