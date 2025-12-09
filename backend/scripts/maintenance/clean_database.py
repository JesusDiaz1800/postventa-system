#!/usr/bin/env python
"""
Script para limpiar completamente la base de datos
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

def clean_database():
    """Limpiar completamente la base de datos"""
    print("🧹 Limpiando base de datos...")
    
    try:
        with connection.cursor() as cursor:
            # Obtener todas las tablas
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                AND TABLE_CATALOG = 'postventa_system'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"📋 Encontradas {len(tables)} tablas")
            
            # Deshabilitar constraints temporalmente
            cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
            
            # Eliminar todas las tablas
            for table in tables:
                try:
                    cursor.execute(f"DROP TABLE [{table}]")
                    print(f"🗑️ Eliminada tabla: {table}")
                except Exception as e:
                    print(f"⚠️ Error eliminando {table}: {e}")
            
            # Rehabilitar constraints
            cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL'")
            
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
        
        print("🎉 Base de datos configurada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    clean_database()
