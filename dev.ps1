# Abre el backend (puerto 8000) y el frontend (puerto 5173) en dos ventanas.
$root = $PSScriptRoot
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root\backend'; & '$root\.venv\Scripts\python.exe' -m uvicorn main:app --reload"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root\frontend'; npm run dev"
Write-Host "Frontend: http://localhost:5173  |  API: http://127.0.0.1:8000/docs"
