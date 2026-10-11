$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$taskRoot=(Get-Location).Path
New-Item -ItemType Directory -Force tmp,data,artifacts | Out-Null
$env:TEMP=Join-Path $taskRoot 'tmp'
$env:TMP=$env:TEMP
$runtime=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies'
if(Test-Path "$runtime\node\bin\node.exe"){$env:PATH="$runtime\node\bin;$runtime\bin\fallback;"+$env:PATH}
if(!(Test-Path '.venv\Scripts\python.exe')){python -m venv .venv;if($LASTEXITCODE){throw 'Virtual environment creation failed'}}
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
if($LASTEXITCODE){throw 'Python dependency installation failed'}
Push-Location frontend
try{
 pnpm install --frozen-lockfile
 if($LASTEXITCODE){throw 'Frontend dependency installation failed'}
 pnpm build
 if($LASTEXITCODE){throw 'Frontend build failed'}
}finally{Pop-Location}
& .\.venv\Scripts\python.exe -m alembic upgrade head
if($LASTEXITCODE){throw 'Database migration failed'}
& .\.venv\Scripts\python.exe scripts\seed.py
if($LASTEXITCODE){throw 'Seed failed'}
Write-Host 'ORION installed. Run scripts/start.ps1. Local login credentials are in .env.'
