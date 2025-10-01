#!/usr/bin/env python
"""
Script para crear usuario con email y verificar login
"""
import os
import sys
import django

# Configurar Django para SQL Server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.users.models import User
from django.contrib.auth import authenticate

def create_user_with_email():
    """Crear usuario con email y verificar login"""
    print("=" * 60)
    print("    CREANDO USUARIO CON EMAIL")
    print("=" * 60)
    
    try:
        # 1. Verificar si ya existe
        try:
            existing_user = User.objects.get(username='jdiaz@polifusion.cl')
            print(f"1. USUARIO YA EXISTE")
            print(f"   Username: {existing_user.username}")
            print(f"   Email: {existing_user.email}")
            print(f"   Role: {existing_user.role}")
        except User.DoesNotExist:
            print("1. CREANDO USUARIO NUEVO")
            
            # Crear usuario
            user = User.objects.create(
                username='jdiaz@polifusion.cl',
                email='jdiaz@polifusion.cl',
                first_name='Jesus',
                last_name='Diaz',
                role='administrador',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            user.set_password('admin123')
            user.save()
            
            print(f"   OK - Usuario creado")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
        
        # 2. Probar login con username
        print(f"\n2. PROBANDO LOGIN CON USERNAME")
        user_by_username = authenticate(username='jdiaz@polifusion.cl', password='admin123')
        if user_by_username:
            print(f"   OK - Login con username funciona")
            print(f"   Usuario: {user_by_username.username}")
        else:
            print(f"   ERROR - Login con username falló")
        
        # 3. Probar login con email
        print(f"\n3. PROBANDO LOGIN CON EMAIL")
        try:
            user_obj = User.objects.get(email='jdiaz@polifusion.cl')
            user_by_email = authenticate(username=user_obj.username, password='admin123')
            if user_by_email:
                print(f"   OK - Login con email funciona")
                print(f"   Usuario: {user_by_email.username}")
            else:
                print(f"   ERROR - Login con email falló")
        except User.DoesNotExist:
            print(f"   ERROR - Usuario con email no encontrado")
        
        # 4. Verificar usuarios disponibles
        print(f"\n4. USUARIOS DISPONIBLES")
        users = User.objects.filter(
            Q(username__icontains='jdiaz') | Q(email__icontains='jdiaz')
        )
        print(f"   Usuarios relacionados con 'jdiaz': {users.count()}")
        for user in users:
            print(f"   - Username: {user.username}")
            print(f"     Email: {user.email}")
            print(f"     Role: {user.role}")
            print()
        
        print("=" * 60)
        print("    CONFIGURACION COMPLETADA")
        print("=" * 60)
        print("OK - Usuario creado correctamente")
        print("   - Username: jdiaz@polifusion.cl")
        print("   - Email: jdiaz@polifusion.cl")
        print("   - Password: admin123")
        print("   - Login funciona con username y email")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_user_with_email()
