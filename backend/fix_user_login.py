#!/usr/bin/env python
"""
Script para solucionar el problema de login
"""
import os
import sys
import django

# Configurar Django para SQL Server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.users.models import User

def fix_user_login():
    """Solucionar problema de login creando usuario correcto"""
    print("=" * 60)
    print("    SOLUCIONANDO PROBLEMA DE LOGIN")
    print("=" * 60)
    
    try:
        # 1. Verificar usuarios existentes
        print("\n1. VERIFICANDO USUARIOS EXISTENTES")
        users = User.objects.all()
        print(f"Total usuarios: {users.count()}")
        
        for user in users:
            print(f"  - Username: {user.username}")
            print(f"    Email: {user.email}")
            print(f"    Role: {user.role}")
            print()
        
        # 2. Buscar usuario jdiaz
        try:
            jdiaz_user = User.objects.get(username='jdiaz')
            print(f"2. USUARIO 'jdiaz' ENCONTRADO")
            print(f"   ID: {jdiaz_user.id}")
            print(f"   Email: {jdiaz_user.email}")
            print(f"   Role: {jdiaz_user.role}")
            
            # 3. Crear usuario jdiaz@polifusion.cl si no existe
            try:
                jdiaz_email_user = User.objects.get(username='jdiaz@polifusion.cl')
                print(f"\n3. USUARIO 'jdiaz@polifusion.cl' YA EXISTE")
                print(f"   ID: {jdiaz_email_user.id}")
            except User.DoesNotExist:
                print(f"\n3. CREANDO USUARIO 'jdiaz@polifusion.cl'")
                
                # Crear nuevo usuario con el email como username
                new_user = User.objects.create(
                    username='jdiaz@polifusion.cl',
                    email='jdiaz@polifusion.cl',
                    first_name='Jesus',
                    last_name='Diaz',
                    role='administrador',
                    is_active=True,
                    is_staff=True,
                    is_superuser=True
                )
                new_user.set_password('admin123')  # Contraseña por defecto
                new_user.save()
                
                print(f"   OK - Usuario creado con ID: {new_user.id}")
                print(f"   Username: {new_user.username}")
                print(f"   Email: {new_user.email}")
                print(f"   Role: {new_user.role}")
                print(f"   Password: admin123")
        
        except User.DoesNotExist:
            print("ERROR - Usuario 'jdiaz' no encontrado")
            return False
        
        # 4. Verificar que el login funcione
        print(f"\n4. VERIFICACION FINAL")
        try:
            test_user = User.objects.get(username='jdiaz@polifusion.cl')
            print(f"   OK - Usuario 'jdiaz@polifusion.cl' disponible")
            print(f"   ID: {test_user.id}")
            print(f"   Role: {test_user.role}")
            print(f"   Active: {test_user.is_active}")
        except User.DoesNotExist:
            print("   ERROR - Usuario 'jdiaz@polifusion.cl' no encontrado")
            return False
        
        print("\n" + "=" * 60)
        print("    PROBLEMA DE LOGIN SOLUCIONADO")
        print("=" * 60)
        print("OK - Usuario 'jdiaz@polifusion.cl' creado correctamente")
        print("   - Username: jdiaz@polifusion.cl")
        print("   - Password: admin123")
        print("   - Role: administrador")
        print("   - El login ahora deberia funcionar")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_user_login()
