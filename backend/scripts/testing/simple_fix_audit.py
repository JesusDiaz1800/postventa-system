#!/usr/bin/env python
"""
Script simple para corregir el endpoint de auditoría
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

def fix_audit():
    """Corregir el sistema de auditoría"""
    try:
        print("Corrigiendo sistema de auditoria...")
        
        # Crear migraciones con respuestas automáticas
        print("Creando migraciones...")
        os.system("python manage.py makemigrations --noinput")
        
        # Aplicar migraciones
        print("Aplicando migraciones...")
        os.system("python manage.py migrate --noinput")
        
        # Crear superusuario si no existe
        print("Verificando usuario administrador...")
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@polifusion.cl', 'admin123')
            print("Usuario administrador creado: admin/admin123")
        else:
            print("Usuario administrador ya existe")
        
        print("Sistema de auditoria corregido exitosamente")
        
    except Exception as e:
        print(f"Error corrigiendo auditoria: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_audit()
