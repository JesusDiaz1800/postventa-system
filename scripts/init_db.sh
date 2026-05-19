#!/bin/bash

# Initialize database script
echo "Initializing Postventa System database..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h localhost -p 5432 -U postventa_user; do
    sleep 1
done

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py shell << EOF
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
    print("Admin user created successfully")
else:
    print("Admin user already exists")
EOF

# Load initial data
echo "Loading initial data..."
python manage.py loaddata initial_data.json

# Create default AI providers
echo "Creating default AI providers..."
python manage.py shell << EOF
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
        print(f"Created AI provider: {provider.name}")
    else:
        print(f"AI provider already exists: {provider.name}")
EOF

# Create default document templates
echo "Creating default document templates..."
python manage.py shell << EOF
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
        print(f"Created template: {template.name}")
    else:
        print(f"Template already exists: {template.name}")
EOF

echo "Database initialization completed successfully!"
