$ErrorActionPreference = 'Stop'
$lessonPython = '.\.venv\Scripts\python.exe'
New-Item -ItemType Directory -Force reports/learning/ci | Out-Null
& $lessonPython -m pytest --collect-only -q | Tee-Object reports/learning/ci/default-collection.txt
if ($LASTEXITCODE -ne 0) { throw '默认测试收集失败' }
& $lessonPython -m pytest --collect-only -q -m real_api | Tee-Object reports/learning/ci/real-api-collection.txt
if ($LASTEXITCODE -ne 0) { throw '公共API收集失败' }
& $lessonPython -m pytest
if ($LASTEXITCODE -ne 0) { throw '默认回归失败' }
