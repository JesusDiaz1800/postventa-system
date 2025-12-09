#!/usr/bin/env python
"""
Script para arreglar la base de datos usando SQL directo
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

def fix_database():
    """Arreglar la base de datos usando SQL directo"""
    print("🔧 Arreglando base de datos...")
    
    try:
        with connection.cursor() as cursor:
            # Eliminar todas las tablas en orden correcto
            print("🗑️ Eliminando tablas...")
            
            # Primero eliminar foreign keys
            cursor.execute("""
                DECLARE @sql NVARCHAR(MAX) = ''
                SELECT @sql = @sql + 'ALTER TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ' DROP CONSTRAINT ' + QUOTENAME(name) + ';'
                FROM sys.foreign_keys
                EXEC sp_executesql @sql
            """)
            
            # Eliminar todas las tablas
            cursor.execute("""
                DECLARE @sql NVARCHAR(MAX) = ''
                SELECT @sql = @sql + 'DROP TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ';'
                FROM sys.tables
                WHERE name NOT LIKE 'sys%'
                EXEC sp_executesql @sql
            """)
            
            print("✅ Tablas eliminadas")
            
        # Aplicar migraciones de Django
        print("📦 Aplicando migraciones de Django...")
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
        
        print("🎉 Base de datos arreglada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    fix_database()
