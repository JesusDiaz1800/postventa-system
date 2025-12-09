#!/usr/bin/env python
"""
Script para crear las tablas sin foreign keys problemáticas
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

def create_tables_simple():
    """Crear las tablas sin foreign keys problemáticas"""
    print("🔧 Creando tablas sin foreign keys...")
    
    try:
        with connection.cursor() as cursor:
            # Crear tabla users
            print("👤 Creando tabla users...")
            cursor.execute("""
                CREATE TABLE users (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    password NVARCHAR(128) NOT NULL,
                    last_login DATETIME2(6),
                    is_superuser BIT NOT NULL DEFAULT 0,
                    username NVARCHAR(150) NOT NULL UNIQUE,
                    first_name NVARCHAR(150) NOT NULL DEFAULT '',
                    last_name NVARCHAR(150) NOT NULL DEFAULT '',
                    email NVARCHAR(254) NOT NULL DEFAULT '',
                    is_staff BIT NOT NULL DEFAULT 0,
                    is_active BIT NOT NULL DEFAULT 1,
                    date_joined DATETIME2(6) NOT NULL DEFAULT GETDATE()
                )
            """)
            
            # Crear tabla django_content_type
            print("📄 Creando tabla django_content_type...")
            cursor.execute("""
                CREATE TABLE django_content_type (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    app_label NVARCHAR(100) NOT NULL,
                    model NVARCHAR(100) NOT NULL
                )
            """)
            
            # Crear tabla django_migrations
            print("📦 Creando tabla django_migrations...")
            cursor.execute("""
                CREATE TABLE django_migrations (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    app NVARCHAR(255) NOT NULL,
                    name NVARCHAR(255) NOT NULL,
                    applied DATETIME2(6) NOT NULL DEFAULT GETDATE()
                )
            """)
            
            # Crear tabla django_session
            print("🔑 Creando tabla django_session...")
            cursor.execute("""
                CREATE TABLE django_session (
                    session_key NVARCHAR(40) PRIMARY KEY,
                    session_data NTEXT NOT NULL,
                    expire_date DATETIME2(6) NOT NULL
                )
            """)
            
            print("✅ Tablas básicas creadas")
            
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
        
        print("🎉 Sistema configurado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    create_tables_simple()
