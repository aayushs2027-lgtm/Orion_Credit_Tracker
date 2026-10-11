$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if(!(Test-Path '.venv\Scripts\python.exe') -or !(Test-Path 'frontend\dist\index.html')){throw 'Run scripts/setup.ps1 first'}
Write-Host 'ORION: http://127.0.0.1:8000 (Ctrl+C to stop)'
& .\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
