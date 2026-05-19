#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.users.models import User
from django.contrib.auth import authenticate

def check_admin():
    """Check and fix admin user"""
    print("🔍 Verificando usuario admin...")
    
    try:
        # Check if admin user exists
        admin_user = User.objects.filter(username='admin').first()
        
        if not admin_user:
            print("❌ Usuario admin no existe. Creándolo...")
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            print("✅ Usuario admin creado exitosamente")
        else:
            print(f"✅ Usuario admin existe: {admin_user.username}")
            
            # Update admin user properties
            admin_user.role = 'admin'
            admin_user.is_active = True
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password('admin123')
            admin_user.save()
            print("✅ Usuario admin actualizado")
        
        # Test authentication
        print("\n🧪 Probando autenticación...")
        user = authenticate(username='admin', password='admin123')
        
        if user:
            print("✅ Autenticación exitosa!")
            print(f"   - Username: {user.username}")
            print(f"   - Role: {user.role}")
            print(f"   - Is Admin: {user.role == 'admin'}")
            print(f"   - Is Active: {user.is_active}")
            print(f"   - Is Staff: {user.is_staff}")
            print(f"   - Is Superuser: {user.is_superuser}")
        else:
            print("❌ Error en autenticación")
            
        # Show all users
        print(f"\n📋 Todos los usuarios en la base de datos:")
        for user in User.objects.all():
            print(f"   - {user.username} (rol: {user.role}, activo: {user.is_active})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_admin()
