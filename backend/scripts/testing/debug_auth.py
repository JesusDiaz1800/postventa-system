#!/usr/bin/env python
"""
Script para debuggear la autenticación
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import requests
import json

def debug_auth():
    """Debuggear la autenticación"""
    try:
        print("Debuggeando autenticación...")
        
        # Verificar usuarios existentes
        users = User.objects.all()
        print(f"Usuarios existentes: {users.count()}")
        
        for user in users:
            print(f"  - {user.username} (active: {user.is_active})")
        
        # Probar autenticación directa
        print("\nProbando autenticación directa...")
        user = authenticate(username='simpleuser', password='simple123')
        if user:
            print(f"Autenticación exitosa: {user.username}")
        else:
            print("Autenticación falló")
        
        # Probar endpoint de debug
        print("\nProbando endpoint de debug...")
        debug_url = "http://localhost:8000/api/auth/debug-auth/"
        response = requests.get(debug_url, timeout=10)
        
        print(f"Debug Status Code: {response.status_code}")
        print(f"Debug Response: {response.text}")
        
        # Probar endpoint de crear usuario
        print("\nProbando endpoint de crear usuario...")
        create_url = "http://localhost:8000/api/auth/debug-create-user/"
        create_data = {
            "username": "debuguser",
            "password": "debug123",
            "email": "debug@polifusion.cl"
        }
        
        create_response = requests.post(create_url, json=create_data, timeout=10)
        print(f"Create Status Code: {create_response.status_code}")
        print(f"Create Response: {create_response.text}")
        
        # Probar login con el nuevo usuario
        if create_response.status_code == 200:
            print("\nProbando login con usuario creado...")
            login_url = "http://localhost:8000/api/auth/login/"
            login_data = {
                "username": "debuguser",
                "password": "debug123"
            }
            
            login_response = requests.post(login_url, json=login_data, timeout=10)
            print(f"Login Status Code: {login_response.status_code}")
            print(f"Login Response: {login_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_auth()
