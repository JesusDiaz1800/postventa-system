#!/usr/bin/env python
"""
Script para probar la eliminación de incidencias
"""
import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.incidents.models import Incident
from apps.users.models import User

def test_delete_incident():
    """Probar eliminación de incidencia directamente en el modelo"""
    print("🧪 Probando eliminación de incidencia directamente...")
    
    try:
        # Obtener una incidencia
        incident = Incident.objects.filter(estado='abierto').first()
        if not incident:
            print("❌ No hay incidencias abiertas para probar")
            return False
        
        print(f"📋 Probando eliminar incidencia: {incident.code} (ID: {incident.id})")
        print(f"📊 Estado actual: {incident.estado}")
        
        # Eliminar la incidencia
        incident_id = incident.id
        incident_code = incident.code
        incident.delete()
        
        print(f"✅ Incidencia eliminada exitosamente")
        print(f"📊 ID eliminado: {incident_id}")
        print(f"📊 Código eliminado: {incident_code}")
        
        # Verificar que se eliminó
        try:
            Incident.objects.get(id=incident_id)
            print("❌ Error: la incidencia aún existe")
            return False
        except Incident.DoesNotExist:
            print("✅ Verificación exitosa: incidencia eliminada")
            return True
        
    except Exception as e:
        print(f"❌ Error eliminando incidencia: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_delete_via_api():
    """Probar eliminación de incidencia vía API"""
    print("\n🧪 Probando eliminación de incidencia vía API...")
    
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
    print("🚀 Iniciando pruebas de eliminación de incidencias...")
    
    # Probar eliminación directa
    direct_success = test_delete_incident()
    
    # Probar eliminación vía API
    api_success = test_delete_via_api()
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print(f"Eliminación directa: {'✅ ÉXITO' if direct_success else '❌ FALLO'}")
    print(f"Eliminación vía API: {'✅ ÉXITO' if api_success else '❌ FALLO'}")
    
    if direct_success and api_success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar los errores arriba.")
