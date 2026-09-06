param(
    [Parameter(Mandatory = $true)]
    [string]$Config
)

$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"
$seeds = 1001, 1002, 1003, 1004, 1005

foreach ($seed in $seeds) {
    & $python -m random_erasing_repro.train --config $Config --seed $seed
    if ($LASTEXITCODE -ne 0) {
        throw "Training failed for seed $seed"
    }
}

& $python -m random_erasing_repro.summarize --config $Config

