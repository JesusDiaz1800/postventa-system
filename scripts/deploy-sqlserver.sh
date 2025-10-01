#!/bin/bash

# Deployment script for Postventa System with SQL Server and Shared Folder
set -e

echo "🚀 Starting deployment of Postventa System with SQL Server..."

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

# Get shared folder path from user
if [ -z "$SHARED_FOLDER_PATH" ]; then
    echo "📁 Please provide the shared folder path:"
    echo "   Examples:"
    echo "   - \\\\servidor\\compartido\\postventa (UNC path)"
    echo "   - C:\\shared\\postventa (Local path)"
    echo "   - /shared/postventa (Linux path)"
    read -p "Enter path: " SHARED_FOLDER_PATH
fi

if [ -z "$SHARED_FOLDER_PATH" ]; then
    echo "❌ Shared folder path is required"
    exit 1
fi

echo "📁 Using shared folder: $SHARED_FOLDER_PATH"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p staticfiles

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/init_db.sh
chmod +x scripts/setup-shared-folder.py

# Copy environment file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📋 Creating environment file..."
    cp backend/env-sqlserver.example backend/.env
    
    # Update shared folder path in .env
    sed -i "s|SHARED_FOLDER_PATH=.*|SHARED_FOLDER_PATH=$SHARED_FOLDER_PATH|g" backend/.env
    
    echo "⚠️  Please edit backend/.env with your configuration before starting the services."
fi

# Setup shared folder structure
echo "📁 Setting up shared folder structure..."
python3 scripts/setup-shared-folder.py "$SHARED_FOLDER_PATH"

# Build and start services
echo "🔨 Building and starting services with SQL Server..."
docker-compose -f docker-compose-sqlserver.yml down --remove-orphans
docker-compose -f docker-compose-sqlserver.yml build --no-cache
docker-compose -f docker-compose-sqlserver.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 60

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose-sqlserver.yml ps

# Initialize database
echo "🗄️  Initializing SQL Server database..."
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py migrate --settings=postventa_system.settings-sqlserver
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py collectstatic --noinput --settings=postventa_system.settings-sqlserver

# Create superuser
echo "👤 Creating superuser..."
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py shell --settings=postventa_system.settings-sqlserver << EOF
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
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py shell --settings=postventa_system.settings-sqlserver << EOF
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
docker-compose -f docker-compose-sqlserver.yml exec -T backend python manage.py shell --settings=postventa_system.settings-sqlserver << EOF
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
docker-compose -f docker-compose-sqlserver.yml ps

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api"
echo "   Admin Panel: http://localhost:8000/admin"
echo "   SQL Server: localhost:1433"
echo ""
echo "👤 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📁 Shared Folder:"
echo "   Path: $SHARED_FOLDER_PATH"
echo "   Structure: documents/, images/, incidents/, templates/, etc."
echo ""
echo "⚠️  Important:"
echo "   1. Change the default admin password"
echo "   2. Configure AI provider API keys in the admin panel"
echo "   3. Review and customize document templates"
echo "   4. Set up email configuration for notifications"
echo "   5. Ensure shared folder has proper network permissions"
echo ""
echo "📚 Documentation: See README.md for detailed usage instructions"
