#!/usr/bin/env python3
"""
Script para configurar la base de datos SQL Server
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

from django.core.management import call_command
from django.contrib.auth import get_user_model

def create_database():
    """Create database if it doesn't exist"""
    print("🔍 Verificando base de datos...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT name FROM sys.databases WHERE name = 'postventa_system'")
            db_exists = cursor.fetchone()
            
            if not db_exists:
                print("📝 Creando base de datos 'postventa_system'...")
                cursor.execute("CREATE DATABASE postventa_system")
                print("✅ Base de datos creada exitosamente!")
            else:
                print("✅ Base de datos 'postventa_system' ya existe.")
                
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False
    
    return True

def run_migrations():
    """Run Django migrations"""
    print("\n🔍 Ejecutando migraciones...")
    
    try:
        # Run migrations
        call_command('migrate', verbosity=1)
        print("✅ Migraciones ejecutadas exitosamente!")
        
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🚀 CONFIGURACIÓN DE BASE DE DATOS SQL SERVER")
    print("=" * 60)
    
    # Step 1: Create database
    if not create_database():
        print("❌ Error creando base de datos. Abortando.")
        return False
    
    # Step 2: Run migrations
    if not run_migrations():
        print("❌ Error ejecutando migraciones. Abortando.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("\n🚀 Próximos pasos:")
    print("1. Iniciar servidor: python manage.py runserver")
    print("2. Acceder a admin: http://localhost:8000/admin")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
