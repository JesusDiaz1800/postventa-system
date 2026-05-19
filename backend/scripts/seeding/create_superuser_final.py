#!/usr/bin/env python
"""
Script para crear superusuario con el modelo correcto
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

def create_superuser_final():
    """Crear superusuario con el modelo correcto"""
    print("👤 Creando superusuario...")
    
    try:
        # Usar el modelo User personalizado
        from apps.users.models import User
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@postventa.com',
                password='admin123'
            )
            print("✅ Superusuario creado: admin/admin123")
        else:
            print("ℹ️ Superusuario ya existe")
        
        print("🎉 Sistema configurado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    create_superuser_final()
