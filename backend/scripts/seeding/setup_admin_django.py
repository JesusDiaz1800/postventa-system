#!/usr/bin/env python
"""
Script para configurar el usuario administrador usando Django ORM
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User as CustomUser

def setup_admin_django():
    """Configurar el usuario administrador usando Django ORM"""
    try:
        print("Configurando usuario administrador real...")
        
        # Crear o actualizar usuario administrador
        user, created = CustomUser.objects.get_or_create(
            username='jdiaz@polifusion.cl',
            defaults={
                'email': 'jdiaz@polifusion.cl',
                'first_name': 'Jesus',
                'last_name': 'Diaz',
                'phone': '+56912345678',  # Teléfono por defecto
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'role': 'admin'
            }
        )
        
        if created:
            user.set_password('adminJDR')
            user.save()
            print("  - Usuario administrador 'jdiaz@polifusion.cl' creado")
        else:
            # Actualizar datos existentes
            user.email = 'jdiaz@polifusion.cl'
            user.first_name = 'Jesus'
            user.last_name = 'Diaz'
            user.phone = '+56912345678'
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.role = 'admin'
            user.set_password('adminJDR')
            user.save()
            print("  - Usuario administrador 'jdiaz@polifusion.cl' actualizado")
        
        print(f"\nUsuario administrador configurado:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Phone: {user.phone}")
        print(f"  Role: {user.role}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        print(f"  Is Active: {user.is_active}")
        
        # Probar autenticación
        print("\nProbando autenticación...")
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='jdiaz@polifusion.cl', password='adminJDR')
        if auth_user:
            print("[OK] Autenticación del administrador exitosa!")
            print(f"Usuario autenticado: {auth_user.username}")
            print(f"Email: {auth_user.email}")
            print(f"Role: {getattr(auth_user, 'role', 'N/A')}")
        else:
            print("[ERROR] Autenticación del administrador falló")
        
        # Mostrar todos los usuarios
        print(f"\nUsuarios en el sistema:")
        users = CustomUser.objects.all()
        for user in users:
            print(f"  - {user.username} ({user.email}) - {user.role}")
        
        print(f"\nTotal de usuarios: {users.count()}")
        
        print(f"\n✅ CONFIGURACIÓN COMPLETADA")
        print(f"📧 Usuario: jdiaz@polifusion.cl")
        print(f"🔑 Contraseña: adminJDR")
        print(f"👤 Nombre: Jesus Diaz")
        print(f"📱 Teléfono: +56912345678")
        print(f"🔧 Rol: Administrador")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_admin_django()
