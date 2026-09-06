param(
    [string]$PythonCommand = "py"
)

$ErrorActionPreference = "Stop"

if ($PythonCommand -eq "py") {
    & py -3.12 -m venv .venv
} else {
    if (-not (Test-Path -LiteralPath $PythonCommand)) {
        throw "Python executable not found: $PythonCommand"
    }
    & $PythonCommand -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install torch==2.12.1 torchvision==0.27.1 --index-url https://download.pytorch.org/whl/cu126
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]" --no-deps
& .\.venv\Scripts\python.exe -m pip install pytest==8.4.2

& .\.venv\Scripts\python.exe -c "import torch, torchvision; print('torch', torch.__version__); print('torchvision', torchvision.__version__); print('cuda', torch.cuda.is_available()); print('device', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
