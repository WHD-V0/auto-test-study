$ErrorActionPreference = 'Stop'
$lessonRoot = (Resolve-Path "$PSScriptRoot/../..").Path
$lessonPython = Join-Path $lessonRoot '.venv/Scripts/python.exe'

function Invoke-LessonJmeter {
    param(
        [Parameter(Mandatory=$true)][string]$Jmeter,
        [Parameter(Mandatory=$true)][string]$Plan,
        [Parameter(Mandatory=$true)][string]$RunName,
        [int]$Threads = 1, [int]$Loops = 3,
        [int]$BusinessRequests = 6, [switch]$ExpectFailure
    )
    if (-not (Test-Path -LiteralPath $Jmeter)) { throw 'JMeter路径不存在' }
    if ($RunName -notmatch '^[A-Za-z0-9-]{1,30}$') { throw 'run_id限30位英数字或连字符' }
    if ($Threads -lt 1 -or $Loops -lt 1) { throw '线程数/循环数必须为正数' }
    $lessonDir = Join-Path $lessonRoot "reports/learning/jmeter/$RunName"
    if (Test-Path -LiteralPath $lessonDir) { throw '结果目录已存在，请换新RunName' }
    New-Item -ItemType Directory -Path $lessonDir | Out-Null
    $lessonHealth = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health
    if ($lessonHealth.StatusCode -ne 200) { throw '靶场未就绪' }
    & $Jmeter -n -t $Plan -q performance/jmeter.properties "-Jthreads=$Threads" "-Jloops=$Loops" "-Jramp_up=$Threads" -Jthink_ms=200 "-Jrun_id=$RunName" -l "$lessonDir/results.jtl" -j "$lessonDir/jmeter.log" -e -o "$lessonDir/html"
    $lessonJmeterExit = $LASTEXITCODE
    if ($lessonJmeterExit -ne 0) { throw "JMeter进程失败：$lessonJmeterExit" }
    $lessonExpected = $Threads * (1 + $BusinessRequests * $Loops)
    & $lessonPython -m tools.check_jtl "$lessonDir/results.jtl" --expected-samples $lessonExpected
    $lessonCheckExit = $LASTEXITCODE
    $lessonSamples = @(Import-Csv -LiteralPath "$lessonDir/results.jtl")
    $lessonFailures = @($lessonSamples | Where-Object { $_.success -eq 'false' }).Count
    if ($ExpectFailure) {
        if ($lessonCheckExit -eq 0 -or $lessonFailures -eq 0) { throw '没有验证到预期断言失败' }
        & $lessonPython -m tools.check_jtl "$lessonDir/results.jtl"
        if ($LASTEXITCODE -eq 0) { throw '包含失败样本却未返回非零' }
        Write-Output "预期故障成立：samples=$($lessonSamples.Count) failures=$lessonFailures"
    } else {
        if ($lessonCheckExit -ne 0) { throw 'JTL数量/断言检查失败' }
        Write-Output "通过：samples=$($lessonSamples.Count) failures=$lessonFailures expected=$lessonExpected"
    }
}

function Remove-LessonTasks {
    param([Parameter(Mandatory=$true)][string]$RunName)
    if ($RunName -notmatch '^[A-Za-z0-9-]{1,30}$') { throw 'run_id非法' }
    $lessonLogin = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/login -ContentType 'application/json' -Body '{"username":"alice","password":"alice-pass"}'
    $lessonHeaders = @{ Authorization = "Bearer $($lessonLogin.token)" }
    $lessonItems = (Invoke-RestMethod -Uri http://127.0.0.1:8765/tasks -Headers $lessonHeaders).items
    $lessonPrefix = "jm-$RunName-"
    $lessonTargets = @($lessonItems | Where-Object { $_.title.StartsWith($lessonPrefix) })
    foreach ($lessonTask in $lessonTargets) {
        Write-Output "清理本轮任务：id=$($lessonTask.id) title=$($lessonTask.title)"
        $lessonDelete = Invoke-WebRequest -UseBasicParsing -Method Delete -Uri "http://127.0.0.1:8765/tasks/$($lessonTask.id)" -Headers $lessonHeaders
        if ($lessonDelete.StatusCode -ne 204) { throw '资源清理失败' }
    }
    $lessonAfter = (Invoke-RestMethod -Uri http://127.0.0.1:8765/tasks -Headers $lessonHeaders).items
    if (@($lessonAfter | Where-Object { $_.title.StartsWith($lessonPrefix) }).Count -ne 0) { throw '仍有本轮残留' }
    Write-Output "run=$RunName 残留检查完成，本次清理$($lessonTargets.Count)条"
}
