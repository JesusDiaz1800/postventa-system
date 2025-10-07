Param(
    [string]$ProjectRoot,
    [string]$BackendHost,
    [int]$BackendPort
)

if (-not $ProjectRoot -or $ProjectRoot -eq '') {
    $ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) | Split-Path -Parent
}
if (-not $BackendHost -or $BackendHost -eq '') { $BackendHost = "0.0.0.0" }
if (-not $BackendPort -or $BackendPort -eq 0) { $BackendPort = 8000 }

Write-Host "=== Postventa System - Start Remoto (Windows) ===" -ForegroundColor Cyan
Set-Location $ProjectRoot

$venvPath = Join-Path $ProjectRoot "backend\.venv"
$python = Join-Path $venvPath "Scripts\python.exe"

if (!(Test-Path $python)) {
    throw "No se encontró el entorno virtual en backend/.venv. Ejecuta scripts/setup-remote.ps1 primero."
}

# Iniciar backend
Write-Host ("Iniciando backend en {0}:{1} ..." -f $BackendHost, $BackendPort) -ForegroundColor Yellow
$argsLine = "`"$ProjectRoot\backend\manage.py`" runserver {0}:{1}" -f $BackendHost, $BackendPort
Start-Process -FilePath $python -ArgumentList $argsLine -NoNewWindow

Write-Host "Backend iniciado. Accede a: http://localhost:$BackendPort/api" -ForegroundColor Green
Write-Host "Swagger: http://localhost:$BackendPort/api/docs" -ForegroundColor Green

Write-Host "Para servir frontend en producción usa Nginx con frontend/nginx.conf o 'npm run preview' en frontend." -ForegroundColor Gray

Exit 0


