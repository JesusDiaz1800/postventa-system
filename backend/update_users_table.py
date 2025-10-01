#!/usr/bin/env python
"""
Script para actualizar la tabla users con los campos faltantes
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

def update_users_table():
    """Actualizar la tabla users con los campos faltantes"""
    print("🔧 Actualizando tabla users...")
    
    try:
        with connection.cursor() as cursor:
            # Agregar campos faltantes
            print("➕ Agregando campo role...")
            cursor.execute("""
                ALTER TABLE users ADD role NVARCHAR(20) NOT NULL DEFAULT 'analyst'
            """)
            
            print("➕ Agregando campo created_at...")
            cursor.execute("""
                ALTER TABLE users ADD created_at DATETIME2(6) NOT NULL DEFAULT GETDATE()
            """)
            
            print("➕ Agregando campo updated_at...")
            cursor.execute("""
                ALTER TABLE users ADD updated_at DATETIME2(6) NOT NULL DEFAULT GETDATE()
            """)
            
            print("➕ Agregando campo phone...")
            cursor.execute("""
                ALTER TABLE users ADD phone NVARCHAR(20) NOT NULL DEFAULT ''
            """)
            
            print("➕ Agregando campo department...")
            cursor.execute("""
                ALTER TABLE users ADD department NVARCHAR(100) NOT NULL DEFAULT ''
            """)
            
            print("✅ Tabla users actualizada")
            
        # Crear superusuario
        print("👤 Creando superusuario...")
        from apps.users.models import User
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@postventa.com',
                password='admin123',
                role='admin'
            )
            print("✅ Superusuario creado: admin/admin123")
        else:
            print("ℹ️ Superusuario ya existe")
        
        print("🎉 Sistema configurado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    update_users_table()
