#!/usr/bin/env python
"""
Script para resetear la base de datos y aplicar migraciones limpias
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

def reset_database():
    """Resetear la base de datos completamente"""
    print("🔄 Reseteando base de datos...")
    
    try:
        # Eliminar todas las tablas
        print("🗑️ Eliminando tablas existentes...")
        execute_from_command_line(['manage.py', 'flush', '--noinput'])
        
        # Aplicar migraciones desde cero
        print("📦 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        
        # Crear superusuario
        print("👤 Creando superusuario...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@postventa.com',
                password='admin123'
            )
            print("✅ Superusuario creado: admin/admin123")
        else:
            print("ℹ️ Superusuario ya existe")
            
        print("🎉 Base de datos reseteada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al resetear base de datos: {e}")
        return False
    
    return True

if __name__ == '__main__':
    reset_database()
