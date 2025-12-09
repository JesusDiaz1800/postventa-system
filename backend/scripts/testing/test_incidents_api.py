import os
import sys
import django
import requests
import json

# Configurar Django para SQL Server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_incidents_api():
    """Probar el endpoint de incidencias con autenticación"""
    print("=== PROBANDO API DE INCIDENCIAS ===")
    
    try:
        # 1. Obtener token de autenticación
        user = User.objects.get(username='jdiaz')
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"Token obtenido para usuario: {user.username}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 2. Probar GET /api/incidents/
        print("\n1. Probando GET /api/incidents/")
        response = requests.get('http://localhost:8000/api/incidents/', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Respuesta completa: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar estructura de respuesta
            if 'results' in data:
                print(f"Incidencias en 'results': {len(data['results'])}")
            elif isinstance(data, list):
                print(f"Incidencias como lista: {len(data)}")
            else:
                print(f"Estructura de respuesta: {type(data)}")
                print(f"Claves disponibles: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
        else:
            print(f"Error: {response.text}")
            
        # 3. Probar endpoint de test
        print("\n2. Probando endpoint de test")
        response = requests.get('http://localhost:8000/api/incidents/test/', headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Test endpoint response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error en test endpoint: {response.text}")

    except User.DoesNotExist:
        print("Error: Usuario 'jdiaz@polifusion.cl' no encontrado.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    test_incidents_api()
