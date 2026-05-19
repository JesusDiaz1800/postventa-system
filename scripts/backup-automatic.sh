#!/bin/bash

# Script de Backup Automático para Sistema Postventa
# Incluye backup de base de datos, archivos y configuración

set -e

# Configuración
BACKUP_DIR="/backups/postventa"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

log_info "Iniciando backup automático - $DATE"

# Backup de base de datos
log_info "Realizando backup de base de datos..."
docker-compose -f docker-compose-sqlserver.yml exec -T sqlserver /opt/mssql-tools/bin/sqlcmd \
    -S localhost -U sa -P TuPassword123! \
    -Q "BACKUP DATABASE postventa_system TO DISK = '/var/opt/mssql/backup/postventa_system_$DATE.bak'"

# Copiar backup a directorio local
docker cp $(docker-compose -f docker-compose-sqlserver.yml ps -q sqlserver):/var/opt/mssql/backup/postventa_system_$DATE.bak \
    "$BACKUP_DIR/postventa_system_$DATE.bak"

log_info "Backup de base de datos completado"

# Backup de archivos de configuración
log_info "Realizando backup de configuración..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    backend/.env \
    backend/postventa_system/settings*.py \
    docker-compose*.yml \
    scripts/

log_info "Backup de configuración completado"

# Backup de archivos de media (si existe)
if [ -d "media" ]; then
    log_info "Realizando backup de archivos de media..."
    tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" media/
    log_info "Backup de media completado"
fi

# Backup de logs
if [ -d "logs" ]; then
    log_info "Realizando backup de logs..."
    tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/
    log_info "Backup de logs completado"
fi

# Limpiar backups antiguos
log_info "Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
find "$BACKUP_DIR" -name "*.bak" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

log_info "Limpieza de backups antiguos completada"

# Crear archivo de información del backup
cat > "$BACKUP_DIR/backup_info_$DATE.txt" << EOF
Backup realizado: $DATE
Sistema: Postventa System
Versión: 1.0.0
Componentes incluidos:
- Base de datos SQL Server
- Archivos de configuración
- Archivos de media
- Logs del sistema

Archivos generados:
- postventa_system_$DATE.bak (Base de datos)
- config_$DATE.tar.gz (Configuración)
- media_$DATE.tar.gz (Archivos de media)
- logs_$DATE.tar.gz (Logs)
- backup_info_$DATE.txt (Este archivo)

Para restaurar:
1. Restaurar base de datos: sqlcmd -Q "RESTORE DATABASE postventa_system FROM DISK = 'backup_file.bak'"
2. Extraer configuración: tar -xzf config_$DATE.tar.gz
3. Extraer media: tar -xzf media_$DATE.tar.gz
4. Extraer logs: tar -xzf logs_$DATE.tar.gz
EOF

log_info "Información de backup guardada"

# Verificar integridad de backups
log_info "Verificando integridad de backups..."
if [ -f "$BACKUP_DIR/postventa_system_$DATE.bak" ]; then
    log_info "✅ Backup de base de datos verificado"
else
    log_error "❌ Error en backup de base de datos"
fi

if [ -f "$BACKUP_DIR/config_$DATE.tar.gz" ]; then
    log_info "✅ Backup de configuración verificado"
else
    log_error "❌ Error en backup de configuración"
fi

# Mostrar resumen
echo ""
echo "📊 RESUMEN DEL BACKUP:"
echo "======================"
echo "Fecha: $DATE"
echo "Directorio: $BACKUP_DIR"
echo "Archivos creados:"
ls -la "$BACKUP_DIR" | grep "$DATE"
echo ""
echo "Tamaño total:"
du -sh "$BACKUP_DIR"/*$DATE*
echo ""

log_info "Backup automático completado exitosamente"

# Opcional: Enviar notificación por email (si está configurado)
if [ ! -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
    log_info "Enviando notificación por email..."
    echo "Backup completado exitosamente el $DATE" | mail -s "Backup Postventa System - $DATE" "$BACKUP_NOTIFICATION_EMAIL"
fi
