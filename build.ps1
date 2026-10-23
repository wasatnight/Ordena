param([string]$Python = "$PSScriptRoot\.venv\Scripts\python.exe")
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& $Python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Tests failed; build stopped' }
& $Python -m PyInstaller --noconfirm --clean --windowed --onedir --name Ordena --noupx main.py
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
Copy-Item README.md, README.es.md, TERCEROS.md dist\Ordena\
Copy-Item -Recurse -Force third-party-licenses dist\Ordena\
Write-Host 'Built dist\Ordena\Ordena.exe. Distribute the entire Ordena folder.'
