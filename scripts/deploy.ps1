# Script de despliegue para el sistema Postventa
param(
    [string]$BackupPath = "C:\backup\postventa",
    [string]$ProjectPath = "C:\postventa-system",
    [string]$LogPath = "C:\logs\postventa"
)

# Función para logging
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path "$LogPath\deploy.log" -Value $logMessage
}

try {
    # Crear directorios necesarios
    $directories = @($BackupPath, $LogPath)
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force
            Write-Log "Creado directorio: $dir"
        }
    }

    # Backup de la base de datos
    $date = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = Join-Path $BackupPath "postventa_$date.bak"
    Write-Log "Iniciando backup de la base de datos..."
    
    $query = "BACKUP DATABASE postventa_system TO DISK='$backupFile'"
    Invoke-Sqlcmd -Query $query -ServerInstance "localhost"
    Write-Log "Backup completado: $backupFile"

    # Detener servicios
    Write-Log "Deteniendo servicios..."
    Stop-Service -Name "PostventaSystem" -ErrorAction SilentlyContinue
    
    # Actualizar código
    Set-Location $ProjectPath
    Write-Log "Actualizando código desde git..."
    git pull origin main

    # Activar entorno virtual
    Write-Log "Activando entorno virtual..."
    & "$ProjectPath\venv\Scripts\Activate.ps1"

    # Instalar dependencias
    Write-Log "Instalando dependencias..."
    pip install -r requirements.txt

    # Configurar variables de entorno
    Write-Log "Configurando variables de entorno..."
    $env:DJANGO_SETTINGS_MODULE = "postventa_system.settings-production"

    # Migraciones
    Write-Log "Aplicando migraciones..."
    python manage.py migrate --noinput

    # Archivos estáticos
    Write-Log "Recolectando archivos estáticos..."
    python manage.py collectstatic --noinput

    # Limpiar caché
    Write-Log "Limpiando caché..."
    python manage.py clearcache

    # Verificar sistema
    Write-Log "Verificando sistema..."
    python manage.py check --deploy

    # Iniciar servicios
    Write-Log "Iniciando servicios..."
    Start-Service -Name "PostventaSystem"

    Write-Log "¡Despliegue completado exitosamente!"

} catch {
    Write-Log "ERROR: $_"
    
    # Intentar restaurar backup si existe
    if (Test-Path $backupFile) {
        Write-Log "Intentando restaurar backup..."
        $restoreQuery = "RESTORE DATABASE postventa_system FROM DISK='$backupFile'"
        Invoke-Sqlcmd -Query $restoreQuery -ServerInstance "localhost"
    }
    
    throw $_
}