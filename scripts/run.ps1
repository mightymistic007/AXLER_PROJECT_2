$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting IceStream Observability Stack" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$venvPython = if (Test-Path ".venv\Scripts\python.exe") {
    Resolve-Path ".venv\Scripts\python.exe"
} elseif (Test-Path "backend\venv\Scripts\python.exe") {
    Resolve-Path "backend\venv\Scripts\python.exe"
} else {
    "python"
}

Write-Host "[*] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath $venvPython -ArgumentList "-m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" -WorkingDirectory "$PSScriptRoot\..\backend" -PassThru

Write-Host "[*] Launching Next.js Dashboard on http://localhost:3000..." -ForegroundColor Green
Start-Process "npm" -ArgumentList "run dev" -WorkingDirectory "$PSScriptRoot\.."

Write-Host "`nIceStream services are starting:" -ForegroundColor Cyan
Write-Host "  - UI Dashboard: http://localhost:3000" -ForegroundColor Yellow
Write-Host "  - REST API & Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C or close the window to stop." -ForegroundColor Gray
