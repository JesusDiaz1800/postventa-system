#!/usr/bin/env python3
"""
Script para restaurar el sistema a su estado funcional anterior
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
from django.db import connection
from django.core.management import execute_from_command_line

User = get_user_model()

def restore_system():
    """Restaurar el sistema a su estado funcional"""
    print("Restaurando sistema a estado funcional...")
    
    # 1. Eliminar base de datos actual
    db_path = "db.sqlite3"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Base de datos anterior eliminada")
    
    # 2. Crear nueva base de datos
    print("Creando nueva base de datos...")
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    
    # 3. Crear usuarios del sistema
    print("Creando usuarios del sistema...")
    
    # Usuario administrador principal
    admin_user, created = User.objects.get_or_create(
        username='jdiaz@polifusion.cl',
        defaults={
            'email': 'jdiaz@polifusion.cl',
            'first_name': 'Jesús',
            'last_name': 'Díaz',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    if created:
        admin_user.set_password('adminJDR')
        admin_user.save()
        print("Usuario administrador creado: jdiaz@polifusion.cl")
    
    # Usuarios adicionales
    users_data = [
        {
            'username': 'admin@polifusion.cl',
            'email': 'admin@polifusion.cl',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'calidad@polifusion.cl',
            'email': 'calidad@polifusion.cl',
            'first_name': 'María',
            'last_name': 'González',
            'password': 'calidad123',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'username': 'ventas@polifusion.cl',
            'email': 'ventas@polifusion.cl',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'password': 'ventas123',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'username': 'tecnico@polifusion.cl',
            'email': 'tecnico@polifusion.cl',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'password': 'tecnico123',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'username': 'cliente1@empresa.cl',
            'email': 'cliente1@empresa.cl',
            'first_name': 'Roberto',
            'last_name': 'Silva',
            'password': 'cliente123',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'cliente2@empresa.cl',
            'email': 'cliente2@empresa.cl',
            'first_name': 'Patricia',
            'last_name': 'López',
            'password': 'cliente123',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'proveedor1@empresa.cl',
            'email': 'proveedor1@empresa.cl',
            'first_name': 'Luis',
            'last_name': 'Hernández',
            'password': 'proveedor123',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'proveedor2@empresa.cl',
            'email': 'proveedor2@empresa.cl',
            'first_name': 'Carmen',
            'last_name': 'Vargas',
            'password': 'proveedor123',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'laboratorio@polifusion.cl',
            'email': 'laboratorio@polifusion.cl',
            'first_name': 'Diego',
            'last_name': 'Morales',
            'password': 'lab123',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'username': 'auditor@polifusion.cl',
            'email': 'auditor@polifusion.cl',
            'first_name': 'Isabel',
            'last_name': 'Castro',
            'password': 'auditor123',
            'is_staff': True,
            'is_superuser': False
        }
    ]
    
    for user_data in users_data:
        password = user_data.pop('password')
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Usuario creado: {user_data['username']}")
    
    # 4. Crear datos de prueba para incidencias
    print("Creando datos de prueba...")
    
    # Crear algunas incidencias de ejemplo
    from apps.incidents.models import Incident
    
    incidents_data = [
        {
            'code': 'INC-2025-001',
            'cliente': 'Empresa ABC S.A.',
            'provider': 'Proveedor XYZ',
            'description': 'Problema con producto defectuoso',
            'status': 'abierto',
            'priority': 'alta',
            'created_by': admin_user
        },
        {
            'code': 'INC-2025-002',
            'cliente': 'Corporación DEF Ltda.',
            'provider': 'Proveedor ABC',
            'description': 'Retraso en entrega',
            'status': 'en_proceso',
            'priority': 'media',
            'created_by': admin_user
        },
        {
            'code': 'INC-2025-003',
            'cliente': 'Industrias GHI S.A.',
            'provider': 'Proveedor DEF',
            'description': 'Calidad no conforme',
            'status': 'abierto',
            'priority': 'alta',
            'created_by': admin_user
        }
    ]
    
    for incident_data in incidents_data:
        incident, created = Incident.objects.get_or_create(
            code=incident_data['code'],
            defaults=incident_data
        )
        if created:
            print(f"Incidencia creada: {incident_data['code']}")
    
    print("Sistema restaurado exitosamente")
    print("Sistema listo para usar")
    print("\nUsuarios disponibles:")
    print("jdiaz@polifusion.cl / adminJDR (Administrador)")
    print("admin@polifusion.cl / admin123 (Administrador)")
    print("calidad@polifusion.cl / calidad123 (Calidad)")
    print("ventas@polifusion.cl / ventas123 (Ventas)")
    print("tecnico@polifusion.cl / tecnico123 (Tecnico)")
    print("laboratorio@polifusion.cl / lab123 (Laboratorio)")
    print("auditor@polifusion.cl / auditor123 (Auditor)")
    print("cliente1@empresa.cl / cliente123 (Cliente)")
    print("cliente2@empresa.cl / cliente123 (Cliente)")
    print("proveedor1@empresa.cl / proveedor123 (Proveedor)")
    print("proveedor2@empresa.cl / proveedor123 (Proveedor)")

if __name__ == '__main__':
    restore_system()
