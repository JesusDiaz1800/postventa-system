#!/usr/bin/env python
"""
Script final para probar el endpoint de auditoría
"""
import requests
import json

def test_audit_endpoint_final():
    """Probar el endpoint de auditoría final"""
    try:
        print("Probando endpoint de auditoría final...")
        
        # Probar endpoint sin autenticación
        print("1. Probando sin autenticación...")
        response = requests.get("http://localhost:8000/api/audit/logs/list/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Probar login
        print("\n2. Probando login...")
        login_response = requests.post("http://localhost:8000/api/auth/login/", 
                                     json={"username": "customuser", "password": "custom123"}, 
                                     timeout=10)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get('success'):
                access_token = login_data.get('access')
                print(f"   Token obtenido: {access_token[:20]}...")
                
                # Probar endpoint con autenticación
                print("\n3. Probando endpoint con autenticación...")
                headers = {"Authorization": f"Bearer {access_token}"}
                audit_response = requests.get("http://localhost:8000/api/audit/logs/list/", 
                                            headers=headers, timeout=10)
                print(f"   Audit Status: {audit_response.status_code}")
                print(f"   Audit Response: {audit_response.text}")
                
                if audit_response.status_code == 200:
                    print("   [OK] Endpoint funcionando correctamente!")
                else:
                    print("   [ERROR] Error en endpoint de auditoría")
            else:
                print(f"   [ERROR] Login falló: {login_data.get('error')}")
        else:
            print(f"   [ERROR] Error en login: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audit_endpoint_final()
