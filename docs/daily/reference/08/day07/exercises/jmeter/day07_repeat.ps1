param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName t2repeat07 -Threads 2 -Loops 10
foreach ($lessonRun in 'smoke03', 'fail04', 'recovered04', 't1day05', 't2day05', 't5day05', 't2repeat07') {
    Remove-LessonTasks -RunName $lessonRun
}
Write-Output '保留重复测量和清理输出；回终端A按Ctrl+C停止本周专用服务。'
