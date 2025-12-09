Param(
    [string]$ProjectRoot,
    [string]$PythonPath,
    [string]$NodeCmd,
    [string]$IpAddress
)

if (-not $ProjectRoot -or $ProjectRoot -eq '') {
    $ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) | Split-Path -Parent
}
if (-not $PythonPath -or $PythonPath -eq '') { $PythonPath = "python" }
if (-not $NodeCmd -or $NodeCmd -eq '') { $NodeCmd = "npm" }
if (-not $IpAddress -or $IpAddress -eq '') { $IpAddress = "192.168.1.234" }

Write-Host "=== Postventa System - Setup Remoto (Windows) ===" -ForegroundColor Cyan
Write-Host "Proyecto: $ProjectRoot" -ForegroundColor Cyan

Set-Location $ProjectRoot

# 1) Crear carpeta compartida local para documentos
$sharedPath = Join-Path $ProjectRoot "shared"
if (!(Test-Path $sharedPath)) {
    New-Item -ItemType Directory -Force -Path $sharedPath | Out-Null
    Write-Host "✔ Carpeta 'shared' creada: $sharedPath" -ForegroundColor Green
} else {
    Write-Host "✔ Carpeta 'shared' ya existe: $sharedPath" -ForegroundColor Green
}

# 2) Backend - crear venv e instalar dependencias
$venvPath = Join-Path $ProjectRoot "backend\.venv"
if (!(Test-Path $venvPath)) {
    & $PythonPath -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el venv" }
}
Write-Host "✔ Entorno virtual listo: $venvPath" -ForegroundColor Green

$pip = Join-Path $venvPath "Scripts\pip.exe"
$python = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Instalando dependencias backend..." -ForegroundColor Yellow
& $pip install --upgrade pip wheel setuptools
& $pip install -r (Join-Path $ProjectRoot "backend\requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Fallo instalando requirements backend" }
Write-Host "✔ Dependencias backend instaladas" -ForegroundColor Green

# 3) Backend - .env
$envExample = Join-Path $ProjectRoot "backend\env.example"
$envFile = Join-Path $ProjectRoot "backend\.env"
if (!(Test-Path $envFile)) {
    Copy-Item $envExample $envFile
}

# Actualizar valores clave en .env
(Get-Content $envFile) |
    ForEach-Object {
        $_ -replace "^DJANGO_ALLOWED_HOSTS=.*","DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,$IpAddress" |
           -replace "^DJANGO_CORS_ALLOWED_ORIGINS=.*","DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://$IpAddress:3000" |
           -replace "^DJANGO_CSRF_TRUSTED_ORIGINS=.*","DJANGO_CSRF_TRUSTED_ORIGINS=http://$IpAddress" |
           -replace "^DEBUG=.*","DEBUG=False" |
           -replace "^DJANGO_ENV=.*","DJANGO_ENV=production" |
           -replace "^SHARED_DOCUMENTS_PATH=.*","SHARED_DOCUMENTS_PATH="
    } | Set-Content $envFile -Encoding UTF8
Write-Host "✔ backend/.env configurado para $IpAddress" -ForegroundColor Green

# 4) Migraciones y collectstatic
Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
& $python (Join-Path $ProjectRoot "backend\manage.py") migrate
if ($LASTEXITCODE -ne 0) { throw "Fallo al ejecutar migraciones" }

Write-Host "Recolectando estáticos..." -ForegroundColor Yellow
& $python (Join-Path $ProjectRoot "backend\manage.py") collectstatic --noinput

# 5) Crear superusuario si no existe (admin/admin123) usando archivo temporal
$tempPy = Join-Path $env:TEMP "create_admin_postventa.py"
$codeLines = @(
    "from apps.users.models import User",
    "try:",
    "    if not User.objects.filter(username='admin').exists():",
    "        User.objects.create_superuser(",
    "            username='admin',",
    "            email='admin@postventa.local',",
    "            password='admin123',",
    "            role='admin'",
    "        )",
    "        print('Admin creado: admin/admin123')",
    "    else:",
    "        print('Admin ya existe')",
    "except Exception as e:",
    "    print('Error creando admin:', e)"
)
$codeLines | Set-Content -Path $tempPy -Encoding UTF8

Write-Host "Verificando/creando superusuario..." -ForegroundColor Yellow
$code = Get-Content -Path $tempPy -Raw
& $python (Join-Path $ProjectRoot "backend\manage.py") shell --command "$code"
Remove-Item -Path $tempPy -ErrorAction SilentlyContinue

# 6) Frontend - instalar y build
Set-Location (Join-Path $ProjectRoot "frontend")
Write-Host "Instalando dependencias frontend..." -ForegroundColor Yellow
& $NodeCmd ci
if ($LASTEXITCODE -ne 0) { & $NodeCmd install }

Write-Host "Construyendo frontend..." -ForegroundColor Yellow
& $NodeCmd run build
if ($LASTEXITCODE -ne 0) { throw "Fallo al hacer build del frontend" }
Write-Host "✔ Frontend construido" -ForegroundColor Green

Write-Host "\n=== Setup completado exitosamente ===" -ForegroundColor Cyan
Write-Host "- Backend: activar venv en backend/.venv" -ForegroundColor Gray
Write-Host "- Iniciar: scripts/start-remote.ps1" -ForegroundColor Gray
Write-Host "- Registrar autoarranque backend: scripts/register-autostart.ps1" -ForegroundColor Gray

Exit 0


