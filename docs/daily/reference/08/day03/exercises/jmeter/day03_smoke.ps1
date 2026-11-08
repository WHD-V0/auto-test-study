param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName smoke03
