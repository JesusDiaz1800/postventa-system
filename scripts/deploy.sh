#!/bin/bash

# Deployment script for Postventa System
set -e

echo "🚀 Starting deployment of Postventa System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p templates

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/init_db.sh
chmod 755 media
chmod 755 staticfiles

# Copy environment file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📋 Creating environment file..."
    cp backend/env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration before starting the services."
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec -T backend python manage.py migrate
docker-compose exec -T backend python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
docker-compose exec -T backend python manage.py shell << EOF
from apps.users.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@postventa.local',
        password='admin123',
        role='admin',
        first_name='Administrador',
        last_name='Sistema'
    )
    print("✅ Admin user created successfully")
else:
    print("ℹ️  Admin user already exists")
EOF

# Create default AI providers
echo "🤖 Creating default AI providers..."
docker-compose exec -T backend python manage.py shell << EOF
from apps.ai_orchestrator.models import AIProvider

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
        print(f"✅ Created AI provider: {provider.name}")
    else:
        print(f"ℹ️  AI provider already exists: {provider.name}")
EOF

# Create default document templates
echo "📄 Creating default document templates..."
docker-compose exec -T backend python manage.py shell << EOF
from apps.documents.models import DocumentTemplate
from apps.users.models import User

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
        print(f"✅ Created template: {template.name}")
    else:
        print(f"ℹ️  Template already exists: {template.name}")
EOF

# Final status check
echo "🔍 Final status check..."
docker-compose ps

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api"
echo "   Admin Panel: http://localhost:8000/admin"
echo "   MinIO Console: http://localhost:9001"
echo ""
echo "👤 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Important:"
echo "   1. Change the default admin password"
echo "   2. Configure AI provider API keys in the admin panel"
echo "   3. Review and customize document templates"
echo "   4. Set up email configuration for notifications"
echo ""
echo "📚 Documentation: See README.md for detailed usage instructions"
