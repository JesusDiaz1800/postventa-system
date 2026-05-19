#!/usr/bin/env python
"""
Script para crear usuario simple y probar
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

def create_simple_user():
    """Crear usuario simple y probar"""
    try:
        print("Creando usuario simple...")
        
        # Eliminar usuario existente si existe
        User.objects.filter(username='simpleuser').delete()
        
        # Crear usuario simple
        user = User.objects.create_user(
            username='simpleuser',
            email='simple@polifusion.cl',
            password='simple123',
            is_staff=True,
            is_superuser=True
        )
        
        print(f"Usuario creado: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print(f"Is Active: {user.is_active}")
        
        # Probar login
        print("\nProbando login...")
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "username": "simpleuser",
            "password": "simple123"
        }
        
        response = requests.post(login_url, json=login_data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
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
                print(f"Audit Status Code: {audit_response.status_code}")
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
    create_simple_user()