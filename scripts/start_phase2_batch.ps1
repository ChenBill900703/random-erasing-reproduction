$ErrorActionPreference = "Stop"

$workspace = (Resolve-Path -LiteralPath ".").Path
$python = Join-Path $workspace ".venv\Scripts\python.exe"
$runs = Join-Path $workspace "runs"
New-Item -ItemType Directory -Force -Path $runs | Out-Null

# Ordered to finish complete baseline/+RE pairs before moving to the next row.
$configs = @(
    "configs/cifar100_resnet20_baseline.toml",
    "configs/cifar100_resnet20_re_paper.toml",
    "configs/fashionmnist_resnet20_baseline.toml",
    "configs/fashionmnist_resnet20_re_paper.toml",
    "configs/cifar10_resnet32_baseline.toml",
    "configs/cifar10_resnet32_re_paper.toml",
    "configs/cifar100_resnet32_baseline.toml",
    "configs/cifar100_resnet32_re_paper.toml",
    "configs/fashionmnist_resnet32_baseline.toml",
    "configs/fashionmnist_resnet32_re_paper.toml"
)

$arguments = @(
    "-u",
    "-m",
    "random_erasing_repro.batch",
    "--status-path",
    "runs/phase2_status.json",
    "--configs"
) + $configs

$process = Start-Process `
    -FilePath $python `
    -ArgumentList $arguments `
    -WorkingDirectory $workspace `
    -RedirectStandardOutput (Join-Path $runs "phase2_stdout.log") `
    -RedirectStandardError (Join-Path $runs "phase2_stderr.log") `
    -WindowStyle Hidden `
    -PassThru

$process.Id | Set-Content -LiteralPath (Join-Path $runs "phase2.pid")
Write-Output "Started Random Erasing phase-2 batch process PID $($process.Id)"
