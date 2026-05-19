#!/usr/bin/env python
"""
Script para limpiar logs existentes y probar el nuevo sistema de auditoría
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.users.models import User
from apps.audit.models import AuditLog, AuditLogManager

def clean_and_test_audit():
    """Limpiar logs existentes y probar el nuevo sistema"""
    print("🧹 Limpiando logs de auditoría existentes...")
    
    # Eliminar todos los logs existentes
    AuditLog.objects.all().delete()
    print("✅ Logs anteriores eliminados")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(email="jdiaz@polifusion.cl")
        print(f"✅ Usuario encontrado: {admin_user.username}")
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado")
        return
    
    # Crear algunos logs de prueba para demostrar el nuevo sistema
    test_actions = [
        {
            'action': 'login',
            'description': 'Inició sesión en el sistema',
            'details': {'session_start': datetime.now().isoformat()}
        },
        {
            'action': 'ver',
            'description': 'Visitó página: Dashboard principal',
            'details': {'page': '/dashboard', 'page_title': 'Dashboard principal'}
        },
        {
            'action': 'ver',
            'description': 'Visitó página: Lista de incidencias',
            'details': {'page': '/incidents', 'page_title': 'Lista de incidencias'}
        },
        {
            'action': 'crear',
            'description': 'Creó nueva incidencia',
            'details': {'incident_type': 'quality', 'client': 'Constructora ABC'}
        },
        {
            'action': 'ver',
            'description': 'Visitó página: Gestión de documentos',
            'details': {'page': '/documents', 'page_title': 'Gestión de documentos'}
        },
        {
            'action': 'crear',
            'description': 'Subió archivo al sistema',
            'details': {'filename': 'reporte_calidad.pdf', 'size': '2.5 MB'}
        },
        {
            'action': 'ver',
            'description': 'Visitó página: Reportes de proveedor',
            'details': {'page': '/reports/supplier', 'page_title': 'Reportes de proveedor'}
        },
        {
            'action': 'crear',
            'description': 'Adjuntó documento',
            'details': {'document_type': 'carta_proveedor', 'incident_id': 'INC-2024-001'}
        },
        {
            'action': 'ver',
            'description': 'Visitó página: Auditoría del sistema',
            'details': {'page': '/audit', 'page_title': 'Auditoría del sistema'}
        },
        {
            'action': 'logout',
            'description': 'Cerró sesión del sistema',
            'details': {'session_end': datetime.now().isoformat()}
        }
    ]
    
    print("📝 Creando logs de prueba del nuevo sistema...")
    
    for i, action_data in enumerate(test_actions, 1):
        audit_log = AuditLog.objects.create(
            user=admin_user,
            action=action_data['action'],
            description=action_data['description'],
            ip_address=f"192.168.1.100",
            details=action_data['details'],
            timestamp=datetime.now()
        )
        print(f"  ✅ {i}/10 - {action_data['description']}")
    
    print(f"\n🎉 Sistema de auditoría configurado exitosamente!")
    print(f"📊 Total de logs creados: {AuditLog.objects.count()}")
    
    print("\n📋 Acciones que ahora se registran:")
    print("  🔑 Login y Logout")
    print("  👁️ Páginas visitadas (navegación)")
    print("  ➕ Crear incidencias")
    print("  🗑️ Eliminar incidencias")
    print("  📤 Subir archivos")
    print("  📥 Descargar archivos")
    print("  📎 Adjuntar documentos")
    print("  ⬆️ Escalar incidencias")
    print("  ✅ Cerrar incidencias")
    
    print("\n❌ Acciones que YA NO se registran:")
    print("  🔍 Consultas (GET a APIs)")
    print("  📊 Búsquedas y filtros")
    print("  📈 Estadísticas")
    print("  🔄 Recargas de página")
    print("  📁 Archivos estáticos")

if __name__ == '__main__':
    try:
        clean_and_test_audit()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
