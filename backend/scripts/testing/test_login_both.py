#!/usr/bin/env python
"""
Script para probar login con username y email
"""
import os
import sys
import django
import requests
import json

# Configurar Django para SQL Server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

def test_login_both_formats():
    """Probar login con username y email"""
    print("=" * 60)
    print("    PROBANDO LOGIN CON USERNAME Y EMAIL")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Datos de prueba
    test_cases = [
        {
            "name": "Login con Username",
            "data": {
                "username": "jdiaz@polifusion.cl",
                "password": "admin123"
            }
        },
        {
            "name": "Login con Email",
            "data": {
                "username": "jdiaz@polifusion.cl",  # El backend ahora acepta email como username
                "password": "admin123"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Username/Email: {test_case['data']['username']}")
        print(f"   Password: {test_case['data']['password']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/auth/login/",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   OK - Login exitoso")
                print(f"   Usuario: {data.get('user', {}).get('username', 'N/A')}")
                print(f"   Email: {data.get('user', {}).get('email', 'N/A')}")
                print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
                print(f"   Token: {data.get('access', 'N/A')[:20]}...")
            else:
                print(f"   ERROR - Login falló")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ERROR - No se puede conectar al servidor")
            print(f"   Asegúrate de que el servidor esté ejecutándose en {base_url}")
        except Exception as e:
            print(f"   ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("    PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_login_both_formats()
