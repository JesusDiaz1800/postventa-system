#!/usr/bin/env python
"""
Script para probar con usuario estándar de Django
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.contrib.auth.models import User as DjangoUser
import requests
import json

def test_standard_user():
    """Probar con usuario estándar de Django"""
    try:
        print("Probando con usuario estándar de Django...")
        
        # Crear usuario estándar de Django
        django_user, created = DjangoUser.objects.get_or_create(
            username='djangouser',
            defaults={
                'email': 'django@polifusion.cl',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            django_user.set_password('django123')
            django_user.save()
            print("Usuario Django creado")
        else:
            django_user.set_password('django123')
            django_user.save()
            print("Usuario Django actualizado")
        
        # Probar autenticación directa
        from django.contrib.auth import authenticate
        user = authenticate(username='djangouser', password='django123')
        if user:
            print("Autenticación directa exitosa")
        else:
            print("Autenticación directa falló")
        
        # Probar login endpoint
        print("\nProbando login endpoint...")
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "username": "djangouser",
            "password": "django123"
        }
        
        response = requests.post(login_url, json=login_data, timeout=10)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("Login exitoso!")
                access_token = data.get('access')
                print(f"Token: {access_token[:20]}...")
                
                # Probar endpoint de auditoría
                print("\nProbando endpoint de auditoría...")
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
    test_standard_user()
