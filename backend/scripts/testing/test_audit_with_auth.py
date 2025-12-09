#!/usr/bin/env python
"""
Script para probar el endpoint de auditoría con autenticación
"""
import requests
import json

def test_audit_with_auth():
    """Probar el endpoint de auditoría con autenticación"""
    try:
        print("Probando endpoint de auditoria con autenticacion...")
        
        # Primero obtener un token válido
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print("Obteniendo token de autenticacion...")
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
        
        # Ahora probar el endpoint de auditoría
        audit_url = "http://localhost:8000/api/audit/logs/list/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Probando endpoint: {audit_url}")
        
        response = requests.get(audit_url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
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
    test_audit_with_auth()
