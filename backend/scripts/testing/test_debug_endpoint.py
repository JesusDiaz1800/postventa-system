"""
Script para probar el endpoint de debugging de documentos compartidos
"""

import requests
import json

def get_auth_token():
    """
    Obtener token de autenticación
    """
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/auth/login/"
    
    # Credenciales de prueba
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"❌ Error de autenticación: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo token: {str(e)}")
        return None

def test_debug_endpoint():
    """
    Probar el endpoint de debugging para ver qué archivos están disponibles
    """
    base_url = "http://localhost:8000"
    
    # Obtener token de autenticación
    token = get_auth_token()
    if not token:
        print("❌ No se pudo obtener token de autenticación")
        return
    
    # Headers con autenticación
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Endpoint de debugging - probar diferentes incidencias
    incident_ids = [76, 77, 78]
    
    for incident_id in incident_ids:
        debug_url = f"{base_url}/api/documents/debug/visit-report/{incident_id}/"
        print(f"\n🔍 Probando incidencia {incident_id}: {debug_url}")
        
        try:
            response = requests.get(debug_url, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Incidencia {incident_id}: {data['count']} archivos")
                if data['files']:
                    for file in data['files']:
                        print(f"  📄 {file['filename']} ({file['size_human']})")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Error en la petición: {str(e)}")

if __name__ == "__main__":
    test_debug_endpoint()
