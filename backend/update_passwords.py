#!/usr/bin/env python3
"""
Script para actualizar contraseñas de usuarios existentes
"""
import os
import sys
import django
import sqlite3
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def update_passwords():
    """Actualizar contraseñas de usuarios existentes"""
    print("Actualizando contraseñas de usuarios...")
    
    # Lista de usuarios y sus nuevas contraseñas
    users_to_update = [
        {
            'username': 'jdiaz@polifusion.cl',
            'password': 'adminJDR',
            'role': 'ADMINISTRADOR'
        },
        {
            'username': 'pestay@polifusion.cl',
            'password': 'Plf2025@',
            'role': 'GERENCIA'
        },
        {
            'username': 'nmingo@gmail.com',
            'password': 'Plf2025@',
            'role': 'GERENCIA'
        },
        {
            'username': 'jpthiry@polifusion.cl',
            'password': 'Plf2025@',
            'role': 'GERENCIA'
        },
        {
            'username': 'srojas@polifusion.cl',
            'password': 'Plf2025@',
            'role': 'GERENCIA'
        },
        {
            'username': 'pmorales@polifusion.cl',
            'password': 'Plf2025#',
            'role': 'SERVICIO TECNICO'
        },
        {
            'username': 'mmontenegro@polifusion.cl',
            'password': 'Plf2025#',
            'role': 'SERVICIO TECNICO'
        },
        {
            'username': 'cmunizaga@polifusion.cl',
            'password': 'Plf2025#',
            'role': 'CALIDAD'
        },
        {
            'username': 'vlutz@polifusion.cl',
            'password': 'Plf2025#',
            'role': 'CALIDAD'
        },
        {
            'username': 'mmiranda@polifusion.cl',
            'password': 'Plf2025#',
            'role': 'CALIDAD'
        },
        {
            'username': 'rcruz@polifusion.cl',
            'password': 'Plf2025#',
            'role': 'CALIDAD'
        }
    ]
    
    updated_count = 0
    
    for user_data in users_to_update:
        try:
            user = User.objects.get(username=user_data['username'])
            user.set_password(user_data['password'])
            user.save()
            print(f"Contraseña actualizada: {user_data['username']} ({user_data['role']})")
            updated_count += 1
        except User.DoesNotExist:
            print(f"Usuario no encontrado: {user_data['username']}")
        except Exception as e:
            print(f"Error actualizando {user_data['username']}: {e}")
    
    print(f"\nTotal de usuarios actualizados: {updated_count}")
    
    # Mostrar usuarios finales
    print("\nUsuarios configurados:")
    print("\nADMINISTRADOR:")
    print("   jdiaz@polifusion.cl / adminJDR")
    
    print("\nGERENCIA (Plf2025@):")
    print("   pestay@polifusion.cl / Plf2025@")
    print("   nmingo@gmail.com / Plf2025@")
    print("   jpthiry@polifusion.cl / Plf2025@")
    print("   srojas@polifusion.cl / Plf2025@")
    
    print("\nSERVICIO TECNICO (Plf2025#):")
    print("   pmorales@polifusion.cl / Plf2025#")
    print("   mmontenegro@polifusion.cl / Plf2025#")
    
    print("\nCALIDAD (Plf2025#):")
    print("   cmunizaga@polifusion.cl / Plf2025#")
    print("   vlutz@polifusion.cl / Plf2025#")
    print("   mmiranda@polifusion.cl / Plf2025#")
    print("   rcruz@polifusion.cl / Plf2025#")
    
    print(f"\nSistema configurado con {updated_count} usuarios específicos")

if __name__ == '__main__':
    update_passwords()
