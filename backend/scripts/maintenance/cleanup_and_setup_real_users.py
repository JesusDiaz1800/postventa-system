#!/usr/bin/env python
"""
Script para limpiar usuarios de prueba y configurar usuarios reales
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User as CustomUser

def cleanup_and_setup_real_users():
    """Limpiar usuarios de prueba y configurar usuarios reales"""
    try:
        print("Limpiando usuarios de prueba...")
        
        # Eliminar usuarios de prueba
        test_users = ['admin', 'testuser', 'simpleuser', 'customuser', 'djangouser', 'debuguser']
        
        for username in test_users:
            try:
                user = CustomUser.objects.get(username=username)
                user.delete()
                print(f"  - Usuario '{username}' eliminado")
            except CustomUser.DoesNotExist:
                print(f"  - Usuario '{username}' no encontrado")
        
        print("\nConfigurando usuario administrador real...")
        
        # Crear usuario administrador real
        admin_user, created = CustomUser.objects.get_or_create(
            username='jdiaz@polifusion.cl',
            defaults={
                'email': 'jdiaz@polifusion.cl',
                'first_name': 'Jesus',
                'last_name': 'Diaz',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'role': 'admin'
            }
        )
        
        if created:
            admin_user.set_password('adminJDR')
            admin_user.save()
            print("  - Usuario administrador 'jdiaz@polifusion.cl' creado")
        else:
            admin_user.set_password('adminJDR')
            admin_user.save()
            print("  - Usuario administrador 'jdiaz@polifusion.cl' actualizado")
        
        print(f"\nUsuario administrador configurado:")
        print(f"  Username: {admin_user.username}")
        print(f"  Email: {admin_user.email}")
        print(f"  Name: {admin_user.first_name} {admin_user.last_name}")
        print(f"  Role: {admin_user.role}")
        print(f"  Is Staff: {admin_user.is_staff}")
        print(f"  Is Superuser: {admin_user.is_superuser}")
        print(f"  Is Active: {admin_user.is_active}")
        
        # Probar autenticación
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='jdiaz@polifusion.cl', password='adminJDR')
        if auth_user:
            print("\n[OK] Autenticación del administrador exitosa!")
        else:
            print("\n[ERROR] Autenticación del administrador falló")
        
        # Mostrar usuarios restantes
        print(f"\nUsuarios en el sistema:")
        users = CustomUser.objects.all()
        for user in users:
            print(f"  - {user.username} ({user.email}) - {user.role}")
        
        print(f"\nTotal de usuarios: {users.count()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_and_setup_real_users()
