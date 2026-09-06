$ErrorActionPreference = "Stop"

$workspace = (Resolve-Path -LiteralPath ".").Path
$python = Join-Path $workspace ".venv\Scripts\python.exe"
$runs = Join-Path $workspace "runs"
New-Item -ItemType Directory -Force -Path $runs | Out-Null

$arguments = @(
    "-u",
    "-m",
    "random_erasing_repro.batch"
)

$process = Start-Process `
    -FilePath $python `
    -ArgumentList $arguments `
    -WorkingDirectory $workspace `
    -RedirectStandardOutput (Join-Path $runs "batch_stdout.log") `
    -RedirectStandardError (Join-Path $runs "batch_stderr.log") `
    -WindowStyle Hidden `
    -PassThru

$process.Id | Set-Content -LiteralPath (Join-Path $runs "batch.pid")
Write-Output "Started Random Erasing batch process PID $($process.Id)"

