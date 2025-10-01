#!/usr/bin/env python
"""
Script para crear usuario administrador
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    """Crear usuario administrador"""
    try:
        print("Creando usuario administrador...")
        
        # Verificar si ya existe
        if User.objects.filter(username='admin').exists():
            print("Usuario administrador ya existe")
            return
        
        # Crear usuario administrador
        user = User.objects.create_superuser(
            username='admin',
            email='admin@polifusion.cl',
            password='admin123'
        )
        
        print("Usuario administrador creado exitosamente:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Is Superuser: {user.is_superuser}")
        print(f"  Is Staff: {user.is_staff}")
        
    except Exception as e:
        print(f"Error creando usuario administrador: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_user()
