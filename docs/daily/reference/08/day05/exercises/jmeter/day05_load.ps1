param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
foreach ($lessonThreads in 1, 2, 5) {
    Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName "t${lessonThreads}day05" -Threads $lessonThreads -Loops 10
}
