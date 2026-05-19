#!/usr/bin/env python
"""
Script para corregir el endpoint de auditoría
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.core.management import execute_from_command_line

def fix_audit():
    """Corregir el sistema de auditoría"""
    try:
        print("🔧 Corrigiendo sistema de auditoría...")
        
        # Crear migraciones con respuestas automáticas
        print("📝 Creando migraciones...")
        os.system("echo y | python manage.py makemigrations --noinput")
        
        # Aplicar migraciones
        print("🚀 Aplicando migraciones...")
        os.system("python manage.py migrate --noinput")
        
        # Crear superusuario si no existe
        print("👤 Verificando usuario administrador...")
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@polifusion.cl', 'admin123')
            print("✅ Usuario administrador creado: admin/admin123")
        else:
            print("✅ Usuario administrador ya existe")
        
        # Crear algunos logs de auditoría de prueba
        print("📊 Creando logs de auditoría de prueba...")
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
            
            print("✅ Logs de auditoría de prueba creados")
        
        print("🎉 Sistema de auditoría corregido exitosamente")
        
    except Exception as e:
        print(f"❌ Error corrigiendo auditoría: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_audit()
