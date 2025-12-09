#!/usr/bin/env python
"""
Script para crear usuario para login
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User as CustomUser

def create_user_for_login():
    """Crear usuario para login"""
    try:
        print("Creando usuario para login...")
        
        # Eliminar usuario existente si existe
        CustomUser.objects.filter(username='admin').delete()
        
        # Crear usuario administrador
        user = CustomUser.objects.create_user(
            username='admin',
            email='admin@polifusion.cl',
            password='admin123',
            is_staff=True,
            is_superuser=True,
            role='admin'
        )
        
        print(f"Usuario creado:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        print(f"  Is Active: {user.is_active}")
        
        # Probar autenticación
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='admin', password='admin123')
        if auth_user:
            print("\n[OK] Autenticación exitosa!")
        else:
            print("\n[ERROR] Autenticación falló")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_user_for_login()
