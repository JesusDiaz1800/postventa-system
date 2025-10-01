#!/usr/bin/env python
"""
Script para probar login con modelo de usuario personalizado
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User as CustomUser
import requests
import json

def test_custom_user_login():
    """Probar login con modelo de usuario personalizado"""
    try:
        print("Probando login con modelo de usuario personalizado...")
        
        # Crear usuario con modelo personalizado
        custom_user, created = CustomUser.objects.get_or_create(
            username='customuser',
            defaults={
                'email': 'custom@polifusion.cl',
                'is_staff': True,
                'is_superuser': True,
                'role': 'admin'
            }
        )
        
        if created:
            custom_user.set_password('custom123')
            custom_user.save()
            print("Usuario personalizado creado")
        else:
            custom_user.set_password('custom123')
            custom_user.save()
            print("Usuario personalizado actualizado")
        
        # Probar autenticación directa
        from django.contrib.auth import authenticate
        user = authenticate(username='customuser', password='custom123')
        if user:
            print("Autenticación directa exitosa")
            print(f"Usuario: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
        else:
            print("Autenticación directa falló")
        
        # Probar login endpoint
        print("\nProbando login endpoint...")
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "username": "customuser",
            "password": "custom123"
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
    test_custom_user_login()
