#!/usr/bin/env python
"""
Script para probar el endpoint de auditoría con JWT
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_audit_with_jwt():
    """Probar el endpoint de auditoría con JWT"""
    try:
        print("Probando endpoint de auditoria con JWT...")
        
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
        
        # Usar Django test client
        client = Client()
        
        # Probar el endpoint con autenticación
        response = client.get(
            '/api/audit/logs/list/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response data: {response.content}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Respuesta exitosa:")
            print(f"   - Success: {data.get('success', 'N/A')}")
            print(f"   - Count: {data.get('count', 'N/A')}")
            print(f"   - Results: {len(data.get('results', []))} elementos")
        else:
            print(f"Error en la respuesta:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Response: {response.content}")
            
    except Exception as e:
        print(f"Error probando endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audit_with_jwt()
