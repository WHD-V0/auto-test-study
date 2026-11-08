param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Jmeter)) { throw '请用-Jmeter参数传入实际jmeter.bat路径' }
java -version
if ($LASTEXITCODE -ne 0) { throw 'Java不可用' }
& $Jmeter -v
if ($LASTEXITCODE -ne 0) { throw 'JMeter不可用' }
$lessonHealth = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health
if ($lessonHealth.StatusCode -ne 200) { throw '靶场未就绪' }
Write-Output 'Java/JMeter可用，靶场health=200；记录真实版本。'
