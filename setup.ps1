# Prepara todo el entorno: Python (.venv), dependencias del backend y del frontend.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) { py -3.11 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
if ((Test-Path "backend\.env.example") -and -not (Test-Path "backend\.env")) { Copy-Item backend\.env.example backend\.env }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Write-Host "Instala Node.js LTS desde https://nodejs.org y vuelve a ejecutar." -ForegroundColor Yellow; exit 1 }
Push-Location frontend; npm install; Pop-Location
Write-Host "Listo. Ejecuta .\dev.ps1" -ForegroundColor Green
