#!/usr/bin/env python
"""
Script para recrear la tabla de auditoría
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connection

def recreate_audit_table():
    """Recrear la tabla de auditoría"""
    print("🗑️ Eliminando tabla audit_auditlog existente...")
    
    with connection.cursor() as cursor:
        # Eliminar tabla si existe
        cursor.execute("DROP TABLE IF EXISTS audit_auditlog;")
        
        # Eliminar migración de la tabla django_migrations
        cursor.execute("DELETE FROM django_migrations WHERE app = 'audit';")
        
        print("✅ Tabla eliminada")
    
    print("🔧 Aplicando migraciones...")
    
    # Aplicar migraciones
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', 'audit'])
    
    print("✅ Tabla recreada exitosamente")

if __name__ == '__main__':
    try:
        recreate_audit_table()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
