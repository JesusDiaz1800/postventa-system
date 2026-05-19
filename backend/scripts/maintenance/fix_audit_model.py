#!/usr/bin/env python
"""
Script para corregir el modelo de auditoría
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

def fix_audit_model():
    """Corregir el modelo de auditoría"""
    try:
        print("Corrigiendo modelo de auditoria...")
        
        # Eliminar la tabla de auditoría si existe
        from django.db import connection
        with connection.cursor() as cursor:
            try:
                cursor.execute("DROP TABLE IF EXISTS audit_logs;")
                print("Tabla audit_logs eliminada")
            except Exception as e:
                print(f"Error eliminando tabla: {e}")
        
        # Ejecutar migraciones específicas
        os.system("python manage.py migrate audit --fake-initial")
        
        # Crear algunos logs de auditoría de prueba
        print("Creando logs de auditoría de prueba...")
        from apps.audit.models import AuditLog
        from django.contrib.auth.models import User
        
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
        
        print("Modelo de auditoría corregido exitosamente")
        
    except Exception as e:
        print(f"Error corrigiendo modelo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_audit_model()
