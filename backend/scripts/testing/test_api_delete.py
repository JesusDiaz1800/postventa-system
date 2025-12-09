#!/usr/bin/env python
"""
Script para probar eliminación vía API
"""
import requests
import json

def test_api_delete():
    """Probar eliminación vía API"""
    print("🧪 Probando eliminación de incidencia vía API...")
    
    try:
        # Obtener token de autenticación
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # Login
        response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            return False
        
        token = response.json().get('access')
        if not token:
            print("❌ No se obtuvo token de acceso")
            return False
        
        print("✅ Login exitoso")
        
        # Obtener incidencias abiertas
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://localhost:8000/api/incidents/?estado=abierto', headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo incidencias: {response.status_code}")
            return False
        
        incidents = response.json().get('results', [])
        if not incidents:
            print("❌ No hay incidencias abiertas")
            return False
        
        # Probar eliminar la primera incidencia
        incident = incidents[0]
        incident_id = incident['id']
        
        print(f"📋 Probando eliminar incidencia: {incident['code']} (ID: {incident_id})")
        
        # Intentar eliminar
        response = requests.delete(f'http://localhost:8000/api/incidents/{incident_id}/', headers=headers)
        
        print(f"📊 Status code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 204:
            print("✅ Incidencia eliminada exitosamente vía API")
            return True
        else:
            print(f"❌ Error eliminando incidencia vía API: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Error en prueba de API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_delete()
