# PowerShell Auto Setup & Run Script for TikTok Affiliate Tool
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "    TOOL TIKTOK AFFILIATE & REUP AUTOMATION - TU DONG CAI DAT & KHOI DONG" -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# 1. Check Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3"
} else {
    Write-Host "[LOI] Khong tim thay Python tren may tinh!" -ForegroundColor Red
    Write-Host "Vui long cai dat Python 3.10 tro len tai: https://www.python.org/downloads/"
    Write-Host "LUU Y: Tich chon vao o 'Add Python to PATH' khi cai dat." -ForegroundColor Yellow
    Read-Host "Nhan Enter de thoat..."
    exit 1
}

Write-Host "[1/5] Kiem tra moi truong Python..." -ForegroundColor Yellow
& $pythonCmd --version

# 2. Check and create virtual environment (.venv)
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[2/5] Chua co moi truong ao .venv. Dang tao .venv..." -ForegroundColor Yellow
    & $pythonCmd -m venv .venv
    Write-Host "[+] Da tao thanh cong thu muc .venv!" -ForegroundColor Green
}

# Activate virtualenv in current session
$venvPython = "$PSScriptRoot\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    $venvPython = $pythonCmd
}

# 3. Install requirements
Write-Host "[3/5] Kiem tra va cai dat thu vien requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r requirements.txt
Write-Host "[+] Thu vien da duoc cai dat day du!" -ForegroundColor Green

# 4. Install Playwright Chromium
Write-Host "[4/5] Kiem tra va tu dong cai dat Playwright Chromium..." -ForegroundColor Yellow
& $venvPython -m playwright install chromium
Write-Host "[+] Playwright Chromium da san sang!" -ForegroundColor Green

# 5. Check .env configuration
Write-Host "[5/5] Kiem tra file cau hinh .env..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[+] Da tao file .env tu .env.example. Vui long kiem tra GEMINI_API_KEY!" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "    TAT CA MOI TRUONG DA SAN SANG! DANG KHOI CHAY CHUONG TRINH..." -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

& $venvPython main.py $args
