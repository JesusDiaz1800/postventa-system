#!/usr/bin/env python
"""
Script para crear administrador y probar endpoint
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.contrib.auth.models import User
import requests
import json

def create_admin_and_test():
    """Crear administrador y probar endpoint"""
    try:
        print("Creando usuario administrador...")
        
        # Crear usuario administrador
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@polifusion.cl',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            print("Usuario administrador creado")
        else:
            print("Usuario administrador ya existe")
        
        # Probar login
        print("Probando login...")
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"Error en login: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        login_data = login_response.json()
        access_token = login_data.get('access')
        
        if not access_token:
            print("No se obtuvo token de acceso")
            return
        
        print(f"Token obtenido: {access_token[:20]}...")
        
        # Probar endpoint de auditoría
        audit_url = "http://localhost:8000/api/audit/logs/list/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Probando endpoint: {audit_url}")
        
        response = requests.get(audit_url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Respuesta exitosa:")
            print(f"   - Success: {data.get('success', 'N/A')}")
            print(f"   - Count: {data.get('count', 'N/A')}")
            print(f"   - Results: {len(data.get('results', []))} elementos")
        else:
            print(f"Error en la respuesta:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Response: {response.text}")
            
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_and_test()
