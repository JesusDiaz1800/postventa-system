#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.users.models import User

def fix_admin_user():
    """Fix admin user role and permissions"""
    try:
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if not created:
            # Update existing admin user
            admin_user.role = 'admin'
            admin_user.is_active = True
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            print(f"✅ Usuario admin actualizado: {admin_user.username} (rol: {admin_user.role})")
        else:
            print(f"✅ Usuario admin creado: {admin_user.username} (rol: {admin_user.role})")
        
        # Set password
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Contraseña establecida: admin123")
        
        # Verify user
        print(f"✅ Usuario verificado:")
        print(f"   - Username: {admin_user.username}")
        print(f"   - Role: {admin_user.role}")
        print(f"   - Is Admin: {admin_user.role == 'admin'}")
        print(f"   - Is Active: {admin_user.is_active}")
        print(f"   - Is Staff: {admin_user.is_staff}")
        print(f"   - Is Superuser: {admin_user.is_superuser}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_admin_user()
