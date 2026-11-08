$ErrorActionPreference = 'Stop'
foreach ($lessonArgs in @(
    @('tests/workflow/test_tasks.py'),
    @('tests/workflow/test_tasks.py', '-n', '2'),
    @('-n', '2')
)) {
    & .\.venv\Scripts\python.exe -m pytest @lessonArgs
    if ($LASTEXITCODE -ne 0) { throw "回归失败：$($lessonArgs -join ' ')" }
}
Write-Output '串行、业务并行、完整并行均通过。自己的extended文件也应按相同方式运行。'
