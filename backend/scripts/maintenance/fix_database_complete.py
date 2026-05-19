#!/usr/bin/env python
"""
Script para corregir completamente la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

def fix_database():
    """Corregir la base de datos completamente"""
    try:
        print("Corrigiendo base de datos...")
        
        # Eliminar archivo de base de datos si existe
        db_file = 'db.sqlite3'
        if os.path.exists(db_file):
            print("Eliminando base de datos existente...")
            os.remove(db_file)
        
        # Ejecutar migraciones
        print("Ejecutando migraciones...")
        os.system("python manage.py migrate --run-syncdb")
        
        # Crear usuario administrador
        print("Creando usuario administrador...")
        from django.contrib.auth.models import User
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@polifusion.cl',
                password='admin123'
            )
            print("Usuario administrador creado exitosamente")
        else:
            print("Usuario administrador ya existe")
        
        # Crear algunos logs de auditoría de prueba
        print("Creando logs de auditoría de prueba...")
        from apps.audit.models import AuditLog
        
        user = User.objects.first()
        if user:
            # Crear algunos logs de prueba
            AuditLog.objects.create(
                user=user,
                action='create',
                resource_type='incident',
                resource_id='1',
                details='Incidente creado para prueba',
                ip_address='127.0.0.1',
                user_agent='Test Agent'
            )
            
            AuditLog.objects.create(
                user=user,
                action='update',
                resource_type='incident',
                resource_id='1',
                details='Incidente actualizado',
                ip_address='127.0.0.1',
                user_agent='Test Agent'
            )
            
            print("Logs de auditoría de prueba creados")
        
        print("Base de datos corregida exitosamente")
        
    except Exception as e:
        print(f"Error corrigiendo base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_database()
