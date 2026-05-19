#!/usr/bin/env python
"""
Script simple para probar el endpoint de auditoría
"""
import requests
import json

def test_audit_endpoint():
    """Probar el endpoint de auditoría"""
    try:
        print("Probando endpoint de auditoria...")
        
        # Probar el endpoint sin autenticación primero
        url = "http://localhost:8000/api/audit/logs/list/"
        
        print(f"Probando endpoint: {url}")
        
        response = requests.get(url, timeout=10)
        
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
    test_audit_endpoint()
