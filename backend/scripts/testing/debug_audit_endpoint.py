#!/usr/bin/env python
"""
Script para debuggear el endpoint de auditoría
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.test import RequestFactory
from apps.audit.views_fixed import audit_logs_list_fixed
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def debug_audit_endpoint():
    """Debuggear el endpoint de auditoría"""
    try:
        print("Debuggeando endpoint de auditoria...")
        
        # Crear un usuario de prueba
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@polifusion.cl',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            print("Usuario de prueba creado")
        else:
            print("Usuario de prueba ya existe")
        
        # Generar token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"Token generado: {access_token[:20]}...")
        
        # Crear request de prueba
        factory = RequestFactory()
        request = factory.get('/api/audit/logs/list/')
        request.user = user
        
        # Probar el endpoint directamente
        print("Probando endpoint directamente...")
        response = audit_logs_list_fixed(request)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response data: {response.data}")
        
    except Exception as e:
        print(f"Error debuggeando endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_audit_endpoint()
