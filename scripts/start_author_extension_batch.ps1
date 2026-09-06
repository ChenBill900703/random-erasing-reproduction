$ErrorActionPreference = "Stop"

$workspace = (Resolve-Path -LiteralPath ".").Path
$python = Join-Path $workspace ".venv\Scripts\python.exe"
$runs = Join-Path $workspace "runs"
New-Item -ItemType Directory -Force -Path $runs | Out-Null

$configs = @(
    "configs/cifar100_resnet20_re_author_code.toml",
    "configs/fashionmnist_resnet20_re_author_code.toml"
)

$arguments = @(
    "-u",
    "-m",
    "random_erasing_repro.batch",
    "--status-path",
    "runs/author_extension_status.json",
    "--configs"
) + $configs

$process = Start-Process `
    -FilePath $python `
    -ArgumentList $arguments `
    -WorkingDirectory $workspace `
    -RedirectStandardOutput (Join-Path $runs "author_extension_stdout.log") `
    -RedirectStandardError (Join-Path $runs "author_extension_stderr.log") `
    -WindowStyle Hidden `
    -PassThru

$process.Id | Set-Content -LiteralPath (Join-Path $runs "author_extension.pid")
Write-Output "Started Random Erasing author-extension batch process PID $($process.Id)"
