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

# Try python-portable first (production), then venv (development)
$pythonPortable = Join-Path $ProjectRoot "python-portable\python\python.exe"
$venvPython = Join-Path $ProjectRoot "backend\.venv\Scripts\python.exe"

if (Test-Path $pythonPortable) {
    $python = $pythonPortable
} elseif (Test-Path $venvPython) {
    $python = $venvPython
} else {
    throw "No se encontró Python. Ejecuta scripts/setup-remote.ps1 primero."
}

# Iniciar backend con Daphne (ASGI + WebSocket)
Write-Host ("Iniciando backend Daphne en {0}:{1} ..." -f $BackendHost, $BackendPort) -ForegroundColor Yellow
Set-Location (Join-Path $ProjectRoot "backend")
$argsLine = "-m daphne -b {0} -p {1} postventa_system.asgi:application" -f $BackendHost, $BackendPort
Start-Process -FilePath $python -ArgumentList $argsLine -NoNewWindow

Write-Host "Backend ASGI iniciado. Accede a: http://localhost:$BackendPort/api" -ForegroundColor Green
Write-Host "WebSocket: ws://localhost:$BackendPort/ws/notifications/" -ForegroundColor Green
Write-Host "Swagger: http://localhost:$BackendPort/api/docs" -ForegroundColor Green

Exit 0
