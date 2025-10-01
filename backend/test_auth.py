#!/usr/bin/env python
import requests
import json

def test_auth():
    """Test authentication endpoints"""
    base_url = "http://localhost:8000/api/auth"
    
    print("🧪 Probando endpoints de autenticación...")
    
    # Test login
    print("\n1. Probando login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/login/", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login exitoso")
            print(f"   Access token: {data.get('access', 'N/A')[:50]}...")
            print(f"   User role: {data.get('user', {}).get('role', 'N/A')}")
            print(f"   User is_admin: {data.get('user', {}).get('is_admin', 'N/A')}")
            
            # Test me endpoint
            print("\n2. Probando endpoint /me/...")
            headers = {
                "Authorization": f"Bearer {data['access']}"
            }
            
            me_response = requests.get(f"{base_url}/me/", headers=headers)
            print(f"   Status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"   ✅ Me endpoint exitoso")
                print(f"   Username: {me_data.get('username', 'N/A')}")
                print(f"   Role: {me_data.get('role', 'N/A')}")
                print(f"   Is Admin: {me_data.get('is_admin', 'N/A')}")
            else:
                print(f"   ❌ Error en /me/: {me_response.text}")
        else:
            print(f"   ❌ Error en login: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

if __name__ == '__main__':
    test_auth()
