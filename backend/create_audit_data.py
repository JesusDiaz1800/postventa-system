#!/usr/bin/env python
"""
Script para crear datos de auditoría de prueba
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.users.models import User
from apps.audit.models import AuditLog

def create_audit_data():
    """Crear datos de auditoría de prueba"""
    print("🔧 Creando datos de auditoría de prueba...")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(email="jdiaz@polifusion.cl")
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado. Ejecuta primero init_data_fix.py")
        return
    
    # Acciones de prueba
    actions = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('create', 'Creación de incidencia'),
        ('update', 'Actualización de incidencia'),
        ('view', 'Visualización de documento'),
        ('upload', 'Subida de archivo'),
        ('download', 'Descarga de archivo'),
        ('export', 'Exportación de datos'),
        ('delete', 'Eliminación de registro'),
    ]
    
    resources = [
        ('incident', 'Incidencia'),
        ('user', 'Usuario'),
        ('document', 'Documento'),
        ('report', 'Reporte'),
        ('system', 'Sistema'),
    ]
    
    severities = ['low', 'medium', 'high', 'critical']
    results = ['success', 'failure', 'partial']
    categories = ['authentication', 'data_access', 'data_modification', 'system_config', 'security']
    
    # Crear logs de auditoría
    for i in range(50):
        action, action_desc = random.choice(actions)
        resource_type, resource_desc = random.choice(resources)
        
        # Crear log de auditoría
        audit_log = AuditLog.objects.create(
            user=admin_user if random.choice([True, False]) else None,
            action=action,
            result=random.choice(results),
            description=f"{action_desc} de {resource_desc}",
            ip_address=f"192.168.1.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            module=resource_type,
            severity=random.choice(severities),
            category=random.choice(categories),
            timestamp=datetime.now() - timedelta(hours=random.randint(0, 168)),  # Última semana
            metadata={
                'browser': 'Chrome',
                'os': 'Windows 10',
                'session_id': f"session_{random.randint(1000, 9999)}"
            }
        )
        
        if i % 10 == 0:
            print(f"✅ Creado log {i+1}/50")
    
    print("🎉 Datos de auditoría creados exitosamente")

if __name__ == '__main__':
    try:
        create_audit_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
