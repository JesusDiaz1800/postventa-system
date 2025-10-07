Write-Host "=== Instalando prerequisitos (winget/choco) ===" -ForegroundColor Cyan

# Intentar con winget
$hasWinget = (Get-Command winget -ErrorAction SilentlyContinue) -ne $null
if ($hasWinget) {
    try { winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements } catch {}
    try { winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements } catch {}
    try { winget install -e --id Microsoft.ODBCDriverForSQLServer --accept-package-agreements --accept-source-agreements } catch {}
} else {
    Write-Host "winget no encontrado. Si usas Chocolatey:" -ForegroundColor Yellow
    Write-Host "choco install python --version=3.12 -y" -ForegroundColor Yellow
    Write-Host "choco install nodejs-lts -y" -ForegroundColor Yellow
    Write-Host "choco install odbcdriver18 -y" -ForegroundColor Yellow
}

Write-Host "Prerequisitos verificados." -ForegroundColor Green
Exit 0


