Param(
    [string]$ProjectRoot
)

if (-not $ProjectRoot -or $ProjectRoot -eq '') {
    $ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) | Split-Path -Parent
}

Set-Location $ProjectRoot

$venvPath = Join-Path $ProjectRoot "backend\.venv"
$python = Join-Path $venvPath "Scripts\python.exe"

if (!(Test-Path $python)) {
    Write-Error "No se encontró el entorno virtual en backend/.venv"
    Exit 1
}

$env:DJANGO_SETTINGS_MODULE = "apps.core.settings"
Start-Process -FilePath $python -ArgumentList "`"$ProjectRoot\backend\manage.py`" runserver 0.0.0.0:8000" -NoNewWindow
Exit 0


