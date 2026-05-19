#!/usr/bin/env python3
"""
Script de inicialización de base de datos para SQL Server
Maneja problemas de migraciones y configuración inicial
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth.models import User

def init_database():
    """Inicializar base de datos con configuración segura"""
    print("🚀 INICIALIZACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Verificar conexión
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexión a base de datos exitosa")
        
        # Crear tablas básicas manualmente
        print("🔧 Creando tablas básicas...")
        
        with connection.cursor() as cursor:
            # Crear tabla de usuarios básica
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
                CREATE TABLE users (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(150) NOT NULL UNIQUE,
                    email NVARCHAR(254) NOT NULL,
                    password NVARCHAR(128) NOT NULL,
                    first_name NVARCHAR(150) NOT NULL,
                    last_name NVARCHAR(150) NOT NULL,
                    is_staff BIT NOT NULL DEFAULT 0,
                    is_active BIT NOT NULL DEFAULT 1,
                    is_superuser BIT NOT NULL DEFAULT 0,
                    date_joined DATETIME2 NOT NULL DEFAULT GETDATE(),
                    last_login DATETIME2 NULL
                )
            """)
            
            # Crear tabla de sesiones
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='django_session' AND xtype='U')
                CREATE TABLE django_session (
                    session_key NVARCHAR(40) PRIMARY KEY,
                    session_data NTEXT NOT NULL,
                    expire_date DATETIME2 NOT NULL
                )
            """)
            
            print("✅ Tablas básicas creadas")
        
        # Crear superusuario
        print("👤 Creando superusuario...")
        
        try:
            # Verificar si ya existe
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
                if cursor.fetchone()[0] > 0:
                    print("✅ Superusuario 'admin' ya existe")
                else:
                    # Crear superusuario
                    from django.contrib.auth.hashers import make_password
                    from django.utils import timezone
                    
                    password = make_password('admin123')
                    now = timezone.now()
                    
                    cursor.execute("""
                        INSERT INTO users (username, email, password, first_name, last_name, 
                                         is_staff, is_active, is_superuser, date_joined)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, ('admin', 'admin@postventa.local', password, 'Admin', 'Sistema', 
                          1, 1, 1, now))
                    
                    print("✅ Superusuario 'admin' creado con contraseña 'admin123'")
        except Exception as e:
            print(f"⚠️  Error creando superusuario: {e}")
        
        print("\n🎉 Base de datos inicializada correctamente")
        print("\n📋 Credenciales de acceso:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("   URL: http://192.168.1.161:8000/admin/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    init_database()
