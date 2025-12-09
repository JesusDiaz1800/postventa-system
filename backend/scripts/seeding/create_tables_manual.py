#!/usr/bin/env python
"""
Script para crear las tablas manualmente en el orden correcto
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

def create_tables_manual():
    """Crear las tablas manualmente en el orden correcto"""
    print("🔧 Creando tablas manualmente...")
    
    try:
        with connection.cursor() as cursor:
            # Crear tabla users primero
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
            
            # Crear tabla auth_group
            print("👥 Creando tabla auth_group...")
            cursor.execute("""
                CREATE TABLE auth_group (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(150) NOT NULL UNIQUE
                )
            """)
            
            # Crear tabla auth_permission
            print("🔐 Creando tabla auth_permission...")
            cursor.execute("""
                CREATE TABLE auth_permission (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(255) NOT NULL,
                    content_type_id INT NOT NULL,
                    codename NVARCHAR(100) NOT NULL
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
            
            # Crear tabla django_admin_log
            print("📝 Creando tabla django_admin_log...")
            cursor.execute("""
                CREATE TABLE django_admin_log (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    action_time DATETIME2(6) NOT NULL DEFAULT GETDATE(),
                    object_id NTEXT,
                    object_repr NVARCHAR(200) NOT NULL,
                    action_flag SMALLINT NOT NULL,
                    change_message NTEXT NOT NULL,
                    content_type_id INT,
                    user_id INT NOT NULL
                )
            """)
            
            # Crear tabla users_groups
            print("👥 Creando tabla users_groups...")
            cursor.execute("""
                CREATE TABLE users_groups (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    user_id INT NOT NULL,
                    group_id INT NOT NULL
                )
            """)
            
            # Crear tabla users_user_permissions
            print("🔐 Creando tabla users_user_permissions...")
            cursor.execute("""
                CREATE TABLE users_user_permissions (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    user_id INT NOT NULL,
                    permission_id INT NOT NULL
                )
            """)
            
            # Crear tabla auth_group_permissions
            print("🔐 Creando tabla auth_group_permissions...")
            cursor.execute("""
                CREATE TABLE auth_group_permissions (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    group_id INT NOT NULL,
                    permission_id INT NOT NULL
                )
            """)
            
            print("✅ Tablas creadas exitosamente")
            
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
    create_tables_manual()
