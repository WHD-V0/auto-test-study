$ErrorActionPreference = 'Stop'
$lessonPython = '.\.venv\Scripts\python.exe'
$lessonDir = 'reports/learning/ci-local'
New-Item -ItemType Directory -Force $lessonDir | Out-Null
& $lessonPython --version
& $lessonPython -m pip freeze | Set-Content -Encoding utf8 "$lessonDir/installed-requirements.txt"
if ($LASTEXITCODE -ne 0) { throw 'freeze失败' }
& $lessonPython -m pytest "--html=$lessonDir/report.html" --self-contained-html "--junitxml=$lessonDir/junit.xml"
$lessonExit = $LASTEXITCODE
Get-Item "$lessonDir/report.html", "$lessonDir/junit.xml", "$lessonDir/installed-requirements.txt"
if ($lessonExit -ne 0) { throw "测试退出码=$lessonExit；请打开失败报告" }
