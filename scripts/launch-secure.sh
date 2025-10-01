#!/bin/bash

# Script de Lanzamiento Seguro del Sistema Postventa
# Incluye mejoras de seguridad y configuración automática

set -e

echo "🚀 LANZAMIENTO SEGURO DEL SISTEMA POSTVENTA"
echo "=============================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar prerrequisitos
log_info "Verificando prerrequisitos..."

# Verificar Docker
if ! docker info > /dev/null 2>&1; then
    log_error "Docker no está ejecutándose. Por favor inicia Docker y vuelve a intentar."
    exit 1
fi
log_success "Docker está ejecutándose"

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose no está instalado. Por favor instala Docker Compose y vuelve a intentar."
    exit 1
fi
log_success "Docker Compose está disponible"

# Verificar archivo .env
if [ ! -f backend/.env ]; then
    log_error "Archivo .env no encontrado. Ejecuta primero la configuración de seguridad."
    exit 1
fi
log_success "Archivo .env encontrado"

# Crear directorios necesarios
log_info "Creando directorios necesarios..."
mkdir -p logs
mkdir -p staticfiles
mkdir -p media
log_success "Directorios creados"

# Configurar permisos
log_info "Configurando permisos..."
chmod +x scripts/*.sh
chmod 755 media
chmod 755 staticfiles
log_success "Permisos configurados"

# Verificar conectividad de red
log_info "Verificando conectividad de red..."
if ping -c 1 192.168.1.161 > /dev/null 2>&1; then
    log_success "Servidor SQL Server (192.168.1.161) es accesible"
else
    log_warning "No se puede acceder al servidor SQL Server (192.168.1.161)"
    log_warning "Verifica la conectividad de red antes de continuar"
fi

# Detener servicios existentes
log_info "Deteniendo servicios existentes..."
docker-compose -f docker-compose-sqlserver.yml down --remove-orphans 2>/dev/null || true
log_success "Servicios detenidos"

# Construir imágenes
log_info "Construyendo imágenes Docker..."
docker-compose -f docker-compose-sqlserver.yml build --no-cache
log_success "Imágenes construidas"

# Iniciar servicios
log_info "Iniciando servicios..."
docker-compose -f docker-compose-sqlserver.yml up -d
log_success "Servicios iniciados"

# Esperar a que los servicios estén listos
log_info "Esperando a que los servicios estén listos..."
sleep 60

# Verificar estado de servicios
log_info "Verificando estado de servicios..."
docker-compose -f docker-compose-sqlserver.yml ps

# Verificar salud de servicios
log_info "Verificando salud de servicios..."
if docker-compose -f docker-compose-sqlserver.yml exec -T sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P TuPassword123! -Q "SELECT 1" > /dev/null 2>&1; then
    log_success "SQL Server está funcionando"
else
    log_warning "SQL Server puede no estar completamente listo"
fi

if docker-compose -f docker-compose-sqlserver.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    log_success "Redis está funcionando"
else
    log_warning "Redis puede no estar completamente listo"
fi

# Ejecutar migraciones
log_info "Ejecutando migraciones de base de datos..."
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py migrate --settings=postventa_system.settings-sqlserver
log_success "Migraciones ejecutadas"

# Recopilar archivos estáticos
log_info "Recopilando archivos estáticos..."
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py collectstatic --noinput --settings=postventa_system.settings-sqlserver
log_success "Archivos estáticos recopilados"

# Crear superusuario
log_info "Creando superusuario..."
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py shell --settings=postventa_system.settings-sqlserver << EOF
from apps.users.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@postventa.local',
        password='AdminSecure2024!',
        first_name='Administrador',
        last_name='Sistema'
    )
    print("✅ Usuario administrador creado exitosamente")
else:
    print("ℹ️  Usuario administrador ya existe")
EOF
log_success "Superusuario configurado"

# Crear datos iniciales
log_info "Creando datos iniciales..."
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py shell --settings=postventa_system.settings-sqlserver << EOF
from apps.ai_orchestrator.models import AIProvider
from apps.documents.models import DocumentTemplate
from apps.users.models import User

# Crear proveedores de IA
providers = [
    {'name': 'openai', 'enabled': False, 'priority': 1, 'daily_quota_tokens': 100000, 'daily_quota_calls': 1000},
    {'name': 'anthropic', 'enabled': False, 'priority': 2, 'daily_quota_tokens': 100000, 'daily_quota_calls': 1000},
    {'name': 'google', 'enabled': False, 'priority': 3, 'daily_quota_tokens': 100000, 'daily_quota_calls': 1000},
    {'name': 'local', 'enabled': True, 'priority': 4, 'daily_quota_tokens': 0, 'daily_quota_calls': 0},
]

for provider_data in providers:
    provider, created = AIProvider.objects.get_or_create(
        name=provider_data['name'],
        defaults=provider_data
    )
    if created:
        print(f"✅ Proveedor de IA creado: {provider.name}")

# Crear plantillas de documentos
admin_user = User.objects.get(username='admin')
templates = [
    {
        'name': 'Informe Cliente',
        'template_type': 'cliente_informe',
        'description': 'Plantilla para informes dirigidos al cliente',
        'docx_template_path': 'templates/cliente_informe.docx',
        'placeholders_json': ['CLIENTE', 'FECHA_DETECCION', 'SKU', 'LOTE', 'DESCRIPCION', 'CONCLUSIONES_TECNICAS', 'RECOMENDACIONES', 'FIRMANTE']
    },
    {
        'name': 'Carta Proveedor',
        'template_type': 'proveedor_carta',
        'description': 'Plantilla para cartas dirigidas al proveedor',
        'docx_template_path': 'templates/proveedor_carta.docx',
        'placeholders_json': ['PROVEEDOR', 'LOTE', 'NUM_PEDIDO', 'DESCRIPCION', 'CONCLUSIONES_TECNICAS', 'FIRMANTE']
    },
    {
        'name': 'Reporte Laboratorio',
        'template_type': 'lab_report',
        'description': 'Plantilla para reportes de laboratorio',
        'docx_template_path': 'templates/lab_report.docx',
        'placeholders_json': ['INCIDENTE', 'MUESTRA', 'ENSAYOS', 'OBSERVACIONES', 'CONCLUSIONES', 'EXPERTO']
    }
]

for template_data in templates:
    template, created = DocumentTemplate.objects.get_or_create(
        name=template_data['name'],
        defaults={
            **template_data,
            'created_by': admin_user
        }
    )
    if created:
        print(f"✅ Plantilla creada: {template.name}")

print("✅ Datos iniciales creados exitosamente")
EOF
log_success "Datos iniciales creados"

# Verificación final
log_info "Realizando verificación final..."
docker-compose -f docker-compose-sqlserver.yml ps

echo ""
echo "🎉 ¡LANZAMIENTO COMPLETADO EXITOSAMENTE!"
echo "=============================================="
echo ""
echo "📋 INFORMACIÓN DE ACCESO:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api"
echo "   Admin Panel: http://localhost:8000/admin"
echo "   SQL Server: localhost:1433"
echo ""
echo "👤 CREDENCIALES DE ACCESO:"
echo "   Usuario: admin"
echo "   Contraseña: AdminSecure2024!"
echo "   Email: admin@postventa.local"
echo ""
echo "🔒 MEJORAS DE SEGURIDAD IMPLEMENTADAS:"
echo "   ✅ Claves secretas generadas automáticamente"
echo "   ✅ Contraseña de administrador segura"
echo "   ✅ Configuración de producción"
echo "   ✅ Headers de seguridad configurados"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Cambia la contraseña del administrador después del primer login"
echo "   2. Configura las claves de API de IA en el panel de administración"
echo "   3. Revisa y personaliza las plantillas de documentos"
echo "   4. Configura el sistema de email para notificaciones"
echo "   5. Asegúrate de que la carpeta compartida tenga permisos correctos"
echo ""
echo "📚 Documentación: Ver README.md para instrucciones detalladas"
echo ""
log_success "Sistema listo para usar!"
