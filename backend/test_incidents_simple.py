#!/usr/bin/env python
"""
Script simple para probar el endpoint de incidencias
"""
import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User as CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

def test_incidents_simple():
    """Probar el endpoint de incidencias de manera simple"""
    try:
        print("Probando endpoint de incidencias...")
        
        # 1. Obtener usuario
        user = CustomUser.objects.get(username='jdiaz@polifusion.cl')
        print(f"Usuario encontrado: {user.username}")
        
        # 2. Obtener token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"Token obtenido: {access_token[:20]}...")
        
        # 3. Probar endpoint de incidencias
        url = "http://localhost:8000/api/incidents/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Realizando petición a: {url}")
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Respuesta exitosa:")
            print(f"Total de incidencias: {data.get('count', 0)}")
            print(f"Resultados: {len(data.get('results', []))}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except CustomUser.DoesNotExist:
        print("Error: Usuario 'jdiaz@polifusion.cl' no encontrado")
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor. Asegúrate de que esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_incidents_simple()
