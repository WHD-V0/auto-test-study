param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow_bad.jmx -RunName fail04 -ExpectFailure
Remove-LessonTasks -RunName fail04
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName recovered04
