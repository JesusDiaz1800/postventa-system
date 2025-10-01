#!/usr/bin/env python
"""
Script para resetear completamente la base de datos
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

def reset_database_complete():
    """Resetear completamente la base de datos"""
    print("🔄 Reseteando base de datos completamente...")
    
    try:
        with connection.cursor() as cursor:
            # Eliminar todas las tablas
            print("🗑️ Eliminando todas las tablas...")
            cursor.execute("""
                DECLARE @sql NVARCHAR(MAX) = ''
                SELECT @sql = @sql + 'DROP TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ';'
                FROM sys.tables
                WHERE name NOT LIKE 'sys%'
                EXEC sp_executesql @sql
            """)
            
            # Eliminar todas las foreign keys
            print("🔗 Eliminando foreign keys...")
            cursor.execute("""
                DECLARE @sql NVARCHAR(MAX) = ''
                SELECT @sql = @sql + 'ALTER TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ' DROP CONSTRAINT ' + QUOTENAME(name) + ';'
                FROM sys.foreign_keys
                EXEC sp_executesql @sql
            """)
            
            print("✅ Base de datos limpiada")
            
        # Aplicar migraciones
        print("📦 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        
        # Crear superusuario
        print("👤 Creando superusuario...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        User.objects.create_superuser(
            username='admin',
            email='admin@postventa.com',
            password='admin123'
        )
        print("✅ Superusuario creado: admin/admin123")
        
        print("🎉 Base de datos reseteada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    reset_database_complete()
