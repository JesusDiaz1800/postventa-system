#!/usr/bin/env python
"""
Script para probar el endpoint de login
"""
import requests
import json

def test_login_endpoint():
    """Probar el endpoint de login"""
    try:
        print("Probando endpoint de login...")
        
        # Probar diferentes credenciales
        credentials = [
            {"username": "admin", "password": "admin123"},
            {"username": "testuser", "password": "test123"},
            {"username": "admin", "password": "admin"},
            {"username": "testuser", "password": "test"},
        ]
        
        for creds in credentials:
            print(f"Probando con usuario: {creds['username']}")
            
            login_url = "http://localhost:8000/api/auth/login/"
            response = requests.post(login_url, json=creds, timeout=10)
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  [OK] Login exitoso con {creds['username']}")
                    return data.get('access')
                else:
                    print(f"  [ERROR] Login falló: {data.get('error')}")
            else:
                print(f"  [ERROR] Error HTTP: {response.status_code}")
            
            print()
        
        print("No se pudo autenticar con ninguna credencial")
        return None
            
    except Exception as e:
        print(f"Error probando login: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_login_endpoint()
