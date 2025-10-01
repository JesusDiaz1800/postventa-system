"""
Script para probar la búsqueda de documentos por nombre
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

def test_search_document():
    """
    Probar la búsqueda de documentos por nombre
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
    
    # Buscar diferentes archivos
    search_files = [
        "OV-20250926-001.pdf",
        "OV-20250926-008.pdf",
        "OV-20250926"
    ]
    
    for filename in search_files:
        search_url = f"{base_url}/api/documents/search/visit-report/{filename}"
        print(f"\n🔍 Buscando: {filename}")
        print(f"URL: {search_url}")
        
        try:
            response = requests.get(search_url, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Encontrados: {data['count']} archivos")
                if data['found_files']:
                    for file in data['found_files']:
                        print(f"  📄 {file['filename']} en incidencia {file['incident_id']} ({file['size_human']})")
                        print(f"     URL: {file['download_url']}")
                else:
                    print("  ❌ No se encontraron archivos")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Error en la petición: {str(e)}")

if __name__ == "__main__":
    test_search_document()
