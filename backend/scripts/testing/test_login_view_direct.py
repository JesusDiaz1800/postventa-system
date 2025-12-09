#!/usr/bin/env python
"""
Script para probar la vista de login directamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.views import login_view
from django.test import RequestFactory
from apps.users.models import User as CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

def test_login_view_direct():
    """Probar la vista de login directamente"""
    try:
        print("Probando vista de login directamente...")
        
        # Crear request de prueba
        factory = RequestFactory()
        request = factory.post('/api/auth/login/', {
            'username': 'customuser',
            'password': 'custom123'
        }, content_type='application/json')
        
        # Simular request.data
        request.data = {
            'username': 'customuser',
            'password': 'custom123'
        }
        
        print(f"Request data: {request.data}")
        
        # Llamar a la vista
        response = login_view(request)
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        if response.status_code == 200:
            data = response.data
            if data.get('success'):
                print("Login exitoso!")
                access_token = data.get('access')
                print(f"Token: {access_token[:20]}...")
                
                # Probar endpoint de auditoría
                print("\nProbando endpoint de auditoría...")
                import requests
                
                audit_url = "http://localhost:8000/api/audit/logs/list/"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                audit_response = requests.get(audit_url, headers=headers, timeout=10)
                print(f"Audit Status: {audit_response.status_code}")
                print(f"Audit Response: {audit_response.text}")
                
            else:
                print(f"Login falló: {data.get('error')}")
        else:
            print(f"Error en login: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_view_direct()
