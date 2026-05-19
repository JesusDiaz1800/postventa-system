#!/usr/bin/env python3
"""
Script para verificar la conexión a SQL Server
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

from django.db import connection
from django.core.management import execute_from_command_line

def test_database_connection():
    """Test database connection"""
    print("🔍 Verificando conexión a la base de datos...")
    print("=" * 50)
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Conexión exitosa a SQL Server!")
            print(f"   Resultado de prueba: {result}")
            
            # Get database info
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"   Versión de SQL Server: {version[0][:100]}...")
            
            # Check if our database exists
            cursor.execute("SELECT name FROM sys.databases WHERE name = 'postventa_system'")
            db_exists = cursor.fetchone()
            if db_exists:
                print("✅ Base de datos 'postventa_system' encontrada!")
            else:
                print("⚠️  Base de datos 'postventa_system' no existe. Se creará automáticamente.")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n🔧 Posibles soluciones:")
        print("1. Verificar que SQL Server esté ejecutándose")
        print("2. Verificar credenciales en .env")
        print("3. Verificar que el puerto 1433 esté abierto")
        print("4. Verificar que la instancia SQLEXPRESS esté disponible")
        return False
    
    return True

def test_django_setup():
    """Test Django setup"""
    print("\n🔍 Verificando configuración de Django...")
    print("=" * 50)
    
    try:
        from django.conf import settings
        print(f"✅ Django configurado correctamente")
        print(f"   Base de datos: {settings.DATABASES['default']['NAME']}")
        print(f"   Host: {settings.DATABASES['default']['HOST']}")
        print(f"   Puerto: {settings.DATABASES['default']['PORT']}")
        print(f"   Usuario: {settings.DATABASES['default']['USER']}")
        
        # Test migrations
        print("\n🔍 Verificando migraciones...")
        from django.core.management import call_command
        call_command('showmigrations', verbosity=0)
        print("✅ Migraciones disponibles")
        
    except Exception as e:
        print(f"❌ Error en configuración de Django: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🚀 VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Test Django setup
    django_ok = test_django_setup()
    
    print("\n" + "=" * 60)
    if db_ok and django_ok:
        print("🎉 ¡CONEXIÓN EXITOSA! El sistema está listo para usar.")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar migraciones: python manage.py migrate")
        print("2. Crear superusuario: python manage.py createsuperuser")
        print("3. Iniciar servidor: python manage.py runserver")
    else:
        print("❌ Hay problemas con la configuración.")
        print("   Revisa los errores anteriores y corrige la configuración.")
    
    return db_ok and django_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
