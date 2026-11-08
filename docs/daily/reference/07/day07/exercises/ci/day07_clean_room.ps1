$ErrorActionPreference = 'Stop'
$lessonRoot = (Get-Location).Path
$lessonDest = Join-Path $lessonRoot 'reports/learning/clean-room'
$lessonZip = Join-Path $lessonRoot 'reports/learning/clean-room.zip'
if (Test-Path $lessonDest) { throw 'clean-room已存在，换新目录名；不要覆盖已有成果' }
New-Item -ItemType Directory -Force (Split-Path $lessonZip) | Out-Null
git archive --format=zip --output=$lessonZip HEAD
if ($LASTEXITCODE -ne 0) { throw 'git archive失败' }
Expand-Archive -LiteralPath $lessonZip -DestinationPath $lessonDest
& .\.venv\Scripts\python.exe -m venv "$lessonDest/.venv"
if ($LASTEXITCODE -ne 0) { throw '干净环境创建失败' }
$lessonPython = Join-Path $lessonDest '.venv/Scripts/python.exe'
Push-Location $lessonDest
try {
    & $lessonPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw '干净环境安装失败' }
    & $lessonPython -m pytest
    if ($LASTEXITCODE -ne 0) { throw '干净环境回归失败' }
} finally {
    Pop-Location
}
Write-Output 'HEAD提交的干净环境可复现；未提交改动不在此副本中。'
