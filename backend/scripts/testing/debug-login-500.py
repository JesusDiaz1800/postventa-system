#!/usr/bin/env python3
"""
Script para diagnosticar el error 500 en POST /api/auth/login/
"""

import requests
import json

def debug_login_500():
    """Diagnosticar el error 500 en login"""
    
    print("DIAGNOSTICO ERROR 500 EN POST /api/auth/login/")
    print("=" * 50)
    
    base_url = "http://192.168.1.234:8000"
    
    # 1. Probar login con diferentes credenciales
    print("\n[1] Probando login con diferentes credenciales...")
    
    test_credentials = [
        {"username": "jdiaz", "password": "adminJDR"},
        {"username": "jdiaz", "password": "adminJDR"},
        {"username": "admin", "password": "admin"},
        {"username": "test", "password": "test"}
    ]
    
    for i, creds in enumerate(test_credentials, 1):
        print(f"\n[{i}] Probando: {creds['username']}")
        try:
            response = requests.post(f"{base_url}/api/auth/login/", json=creds, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("[OK] Login exitoso")
                token_data = response.json()
                print(f"Token: {token_data.get('access', 'N/A')[:30]}...")
                break
            elif response.status_code == 500:
                print("[ERROR] Error 500 - Error interno del servidor")
                try:
                    error_data = response.json()
                    print("Error details:", error_data)
                except:
                    print("Response text:", response.text)
            else:
                print(f"[WARNING] Status inesperado: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Excepción: {e}")
    
    # 2. Verificar si el servidor está funcionando
    print(f"\n[2] Verificando servidor...")
    try:
        response = requests.get(f"{base_url}/api/", timeout=5)
        print(f"Servidor status: {response.status_code}")
        if response.status_code == 200:
            print("[OK] Servidor funcionando")
        else:
            print(f"[WARNING] Servidor responde con: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Servidor no disponible: {e}")
    
    # 3. Verificar endpoint de usuarios
    print(f"\n[3] Verificando endpoint de usuarios...")
    try:
        response = requests.get(f"{base_url}/api/users/", timeout=5)
        print(f"Usuarios status: {response.status_code}")
        if response.status_code == 200:
            print("[OK] Endpoint de usuarios funcionando")
        else:
            print(f"[WARNING] Usuarios responde con: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error en usuarios: {e}")
    
    # 4. Probar con datos de login diferentes
    print(f"\n[4] Probando con diferentes formatos de datos...")
    
    test_formats = [
        {"username": "jdiaz", "password": "adminJDR"},
        {"email": "jdiaz@polifusion.cl", "password": "adminJDR"},
        {"user": "jdiaz", "pass": "adminJDR"}
    ]
    
    for i, data in enumerate(test_formats, 1):
        print(f"\n[{i}] Formato: {list(data.keys())}")
        try:
            response = requests.post(f"{base_url}/api/auth/login/", json=data, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("[OK] Login exitoso con este formato")
                break
            else:
                print(f"Response: {response.text[:100]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_login_500()
