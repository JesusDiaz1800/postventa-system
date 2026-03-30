Param(
    [string]$ProjectRoot
)

if (-not $ProjectRoot -or $ProjectRoot -eq '') {
    $ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) | Split-Path -Parent
}

Set-Location $ProjectRoot

# Try python-portable first (production), then venv (development)
$pythonPortable = Join-Path $ProjectRoot "python-portable\python\python.exe"
$venvPython = Join-Path $ProjectRoot "backend\.venv\Scripts\python.exe"

if (Test-Path $pythonPortable) {
    $python = $pythonPortable
} elseif (Test-Path $venvPython) {
    $python = $venvPython
} else {
    Write-Error "No se encontró Python (ni python-portable ni backend/.venv)"
    Exit 1
}

$env:DJANGO_SETTINGS_MODULE = "apps.core.settings"

# IMPORTANT: Use Daphne (ASGI) instead of runserver to enable WebSocket support
Write-Host "Iniciando backend con Daphne (ASGI + WebSocket)..." -ForegroundColor Cyan
Set-Location (Join-Path $ProjectRoot "backend")
Start-Process -FilePath $python -ArgumentList "-m daphne -b 0.0.0.0 -p 8000 postventa_system.asgi:application" -NoNewWindow
Exit 0
