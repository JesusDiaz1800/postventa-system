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

def create_superuser():
    """Create superuser if it doesn't exist"""
    print("\n🔍 Verificando superusuario...")
    
    try:
        User = get_user_model()
        
        # Check if superuser exists
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superusuario ya existe.")
            return True
        
        print("📝 Creando superusuario...")
        print("   Usuario: admin")
        print("   Email: admin@postventa.local")
        print("   Contraseña: admin123")
        
        # Create superuser
        User.objects.create_superuser(
            username='admin',
            email='admin@postventa.local',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        
        print("✅ Superusuario creado exitosamente!")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False
    
    return True

def create_initial_data():
    """Create initial data"""
    print("\n🔍 Creando datos iniciales...")
    
    try:
        # Create roles
        from apps.users.models import User
        from django.contrib.auth.models import Group
        
        # Create groups for roles
        roles = [
            ('admin', 'Administrador'),
            ('supervisor', 'Supervisor'),
            ('analista', 'Analista Técnico'),
            ('atencion_cliente', 'Atención al Cliente'),
            ('proveedor', 'Proveedor'),
        ]
        
        for role_code, role_name in roles:
            group, created = Group.objects.get_or_create(name=role_code)
            if created:
                print(f"   ✅ Rol '{role_name}' creado")
            else:
                print(f"   ✅ Rol '{role_name}' ya existe")
        
        # Create sample users
        sample_users = [
            ('supervisor1', 'supervisor1@postventa.local', 'Supervisor', 'Uno', 'supervisor'),
            ('analista1', 'analista1@postventa.local', 'Analista', 'Uno', 'analista'),
            ('atencion1', 'atencion1@postventa.local', 'Atención', 'Uno', 'atencion_cliente'),
        ]
        
        for username, email, first_name, last_name, role in sample_users:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name
                )
                group = Group.objects.get(name=role)
                user.groups.add(group)
                print(f"   ✅ Usuario '{username}' creado")
            else:
                print(f"   ✅ Usuario '{username}' ya existe")
        
        print("✅ Datos iniciales creados exitosamente!")
        
    except Exception as e:
        print(f"❌ Error creando datos iniciales: {e}")
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
    
    # Step 3: Create superuser
    if not create_superuser():
        print("❌ Error creando superusuario. Abortando.")
        return False
    
    # Step 4: Create initial data
    if not create_initial_data():
        print("❌ Error creando datos iniciales. Abortando.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("\n📋 Información de acceso:")
    print("   Usuario administrador: admin")
    print("   Contraseña: admin123")
    print("   Email: admin@postventa.local")
    print("\n🚀 Próximos pasos:")
    print("1. Iniciar servidor: python manage.py runserver")
    print("2. Acceder a admin: http://localhost:8000/admin")
    print("3. Acceder a API: http://localhost:8000/api")
    print("4. Iniciar frontend: cd ../frontend && npm run dev")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
