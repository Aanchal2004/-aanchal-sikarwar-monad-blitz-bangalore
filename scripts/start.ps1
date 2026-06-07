# PowerShell startup script for Windows
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — add your API keys!"
}

Write-Host "Starting backend on :8000..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\backend'; uvicorn app:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

Write-Host "Starting frontend on :3000..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\frontend'; npm run dev"

Write-Host ""
Write-Host "Backend:  http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000"
