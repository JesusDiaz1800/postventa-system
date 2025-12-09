import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_frontend_incidents():
    """Probar el endpoint como lo hace el frontend"""
    print("=== PROBANDO ENDPOINT COMO FRONTEND ===")
    
    try:
        # 1. Obtener token de autenticación
        user = User.objects.get(username='jdiaz@polifusion.cl')
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"Token obtenido para usuario: {user.username}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 2. Probar GET /api/incidents/ con diferentes parámetros
        print("\n1. Probando GET /api/incidents/ (sin filtros)")
        response = requests.get('http://localhost:8000/api/incidents/', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo de respuesta: {type(data)}")
            print(f"Longitud: {len(data) if isinstance(data, list) else 'No es lista'}")
            
            if isinstance(data, list):
                print(f"Incidencias encontradas: {len(data)}")
                for i, incident in enumerate(data):
                    print(f"  {i+1}. {incident.get('code', 'Sin código')} - {incident.get('cliente', 'Sin cliente')}")
            else:
                print(f"Estructura de respuesta: {data}")
        
        # 3. Probar con filtros
        print("\n2. Probando GET /api/incidents/?estado=abierto")
        response = requests.get('http://localhost:8000/api/incidents/?estado=abierto', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Incidencias con estado 'abierto': {len(data) if isinstance(data, list) else 'No es lista'}")
        
        # 4. Probar con filtro de prioridad
        print("\n3. Probando GET /api/incidents/?prioridad=media")
        response = requests.get('http://localhost:8000/api/incidents/?prioridad=media', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Incidencias con prioridad 'media': {len(data) if isinstance(data, list) else 'No es lista'}")
        
        # 5. Verificar si hay incidencias cerradas
        print("\n4. Probando GET /api/incidents/?estado=cerrado")
        response = requests.get('http://localhost:8000/api/incidents/?estado=cerrado', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Incidencias con estado 'cerrado': {len(data) if isinstance(data, list) else 'No es lista'}")
        
        # 6. Verificar si hay incidencias con diferentes prioridades
        print("\n5. Verificando todas las prioridades")
        for prioridad in ['baja', 'media', 'alta', 'critica']:
            response = requests.get(f'http://localhost:8000/api/incidents/?prioridad={prioridad}', headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"  Prioridad '{prioridad}': {count} incidencias")
        
    except User.DoesNotExist:
        print("Error: Usuario 'jdiaz@polifusion.cl' no encontrado.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_incidents()
