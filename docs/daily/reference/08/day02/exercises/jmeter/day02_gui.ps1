param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Jmeter)) { throw 'JMeter路径错误' }
& $Jmeter -t performance/my_task_workflow.jmx
if ($LASTEXITCODE -ne 0) { throw 'GUI启动/运行异常，查看JMeter日志' }
