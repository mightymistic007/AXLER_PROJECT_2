$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " IceStream: Lakehouse Control Plane Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Environment file setup
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[+] Created .env from .env.example" -ForegroundColor Green
    }
} else {
    Write-Host "[*] .env profile already exists" -ForegroundColor Gray
}

# 2. Python Virtual Environment
$venvPython = if (Test-Path ".venv\Scripts\python.exe") {
    ".venv\Scripts\python.exe"
} elseif (Test-Path "backend\venv\Scripts\python.exe") {
    "backend\venv\Scripts\python.exe"
} else {
    Write-Host "[*] Creating Python virtual environment in .venv..." -ForegroundColor Yellow
    python -m venv .venv
    ".venv\Scripts\python.exe"
}

Write-Host "[*] Installing Python backend dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r backend/requirements-dev.txt --quiet
Write-Host "[+] Backend dependencies installed successfully" -ForegroundColor Green

# 3. Frontend npm setup
Write-Host "[*] Installing Node.js frontend dependencies..." -ForegroundColor Yellow
npm install
Write-Host "[+] Frontend dependencies installed successfully" -ForegroundColor Green

Write-Host "`nSetup complete! You can now start the application with:" -ForegroundColor Cyan
Write-Host "  .\scripts\run.ps1" -ForegroundColor Yellow
Write-Host "Or in VS Code: Run Task -> IceStream: Start all" -ForegroundColor Yellow
Write-Host "`nLocal credentials: username: axlero.operator | user_id: AXL-IS-001 | password: IceStream@2026" -ForegroundColor Gray
