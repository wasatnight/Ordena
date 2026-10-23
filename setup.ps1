param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& $Python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Could not create .venv' }
& .\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
Write-Host 'Ready: .\.venv\Scripts\python.exe main.py'
