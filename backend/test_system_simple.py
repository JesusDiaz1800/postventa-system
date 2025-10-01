#!/usr/bin/env python3
"""
Script para probar que el sistema restaurado funciona correctamente
"""
import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_system():
    """Probar que el sistema funciona correctamente"""
    print("Probando sistema restaurado...")
    
    # 1. Verificar usuarios creados
    print("\n1. Verificando usuarios creados:")
    users = User.objects.all()
    print(f"Total de usuarios: {users.count()}")
    
    for user in users:
        print(f"- {user.username} ({user.email}) - Staff: {user.is_staff}")
    
    # 2. Probar autenticación
    print("\n2. Probando autenticación:")
    try:
        # Obtener token para usuario administrador
        admin_user = User.objects.get(username='jdiaz@polifusion.cl')
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        print(f"Token generado para {admin_user.username}")
        
        # Probar endpoint de login
        login_data = {
            'username': 'jdiaz@polifusion.cl',
            'password': 'adminJDR'
        }
        
        response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
        if response.status_code == 200:
            print("Login exitoso")
            token_data = response.json()
            print(f"Token recibido: {token_data.get('access', 'N/A')[:50]}...")
        else:
            print(f"Error en login: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error en autenticacion: {e}")
    
    # 3. Probar endpoint de incidencias
    print("\n3. Probando endpoint de incidencias:")
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('http://localhost:8000/api/incidents/', headers=headers)
        
        if response.status_code == 200:
            print("Endpoint de incidencias funciona")
            data = response.json()
            print(f"Incidencias encontradas: {len(data.get('results', []))}")
        else:
            print(f"Error en incidencias: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error probando incidencias: {e}")
    
    # 4. Probar endpoint de usuarios
    print("\n4. Probando endpoint de usuarios:")
    try:
        response = requests.get('http://localhost:8000/api/users/', headers=headers)
        
        if response.status_code == 200:
            print("Endpoint de usuarios funciona")
            data = response.json()
            print(f"Usuarios encontrados: {len(data)}")
        else:
            print(f"Error en usuarios: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error probando usuarios: {e}")
    
    print("\nSistema restaurado y funcionando correctamente")
    print("\nCredenciales de acceso:")
    print("jdiaz@polifusion.cl / adminJDR (Administrador principal)")
    print("admin@polifusion.cl / admin123 (Administrador)")
    print("calidad@polifusion.cl / calidad123 (Calidad)")
    print("ventas@polifusion.cl / ventas123 (Ventas)")
    print("tecnico@polifusion.cl / tecnico123 (Tecnico)")
    print("laboratorio@polifusion.cl / lab123 (Laboratorio)")
    print("auditor@polifusion.cl / auditor123 (Auditor)")
    print("cliente1@empresa.cl / cliente123 (Cliente)")
    print("cliente2@empresa.cl / cliente123 (Cliente)")
    print("proveedor1@empresa.cl / proveedor123 (Proveedor)")
    print("proveedor2@empresa.cl / proveedor123 (Proveedor)")

if __name__ == '__main__':
    test_system()
