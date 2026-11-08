param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_archive_workflow.jmx -RunName archive06 -BusinessRequests 8
Remove-LessonTasks -RunName archive06
