#!/usr/bin/env python
"""
Script de prueba para verificar el cierre de incidencias
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

def test_close_incident():
    """Probar cierre de incidencia directamente en el modelo"""
    print("🧪 Probando cierre de incidencia directamente...")
    
    try:
        # Obtener una incidencia abierta
        incident = Incident.objects.filter(estado='abierto').first()
        if not incident:
            print("❌ No hay incidencias abiertas para probar")
            return False
        
        print(f"📋 Probando con incidencia: {incident.code} (ID: {incident.id})")
        print(f"📊 Estado actual: {incident.estado}")
        
        # Obtener un usuario
        user = User.objects.first()
        if not user:
            print("❌ No hay usuarios en el sistema")
            return False
        
        print(f"👤 Usuario: {user.username}")
        
        # Simular el cierre
        incident.estado = 'cerrado'
        incident.closed_by = user
        incident.closed_at = django.utils.timezone.now()
        incident.fecha_cierre = django.utils.timezone.now().date()
        incident.save()
        
        print(f"✅ Incidencia cerrada exitosamente")
        print(f"📊 Nuevo estado: {incident.estado}")
        print(f"📅 Fecha de cierre: {incident.fecha_cierre}")
        print(f"👤 Cerrado por: {incident.closed_by.username if incident.closed_by else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cerrando incidencia: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_close_via_api():
    """Probar cierre de incidencia vía API"""
    print("\n🧪 Probando cierre de incidencia vía API...")
    
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
        
        # Probar cerrar la primera incidencia
        incident = incidents[0]
        incident_id = incident['id']
        
        print(f"📋 Probando cerrar incidencia: {incident['code']} (ID: {incident_id})")
        
        # Intentar cerrar
        response = requests.post(f'http://localhost:8000/api/incidents/{incident_id}/close/', headers=headers)
        
        print(f"📊 Status code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Incidencia cerrada exitosamente vía API")
            return True
        else:
            print(f"❌ Error cerrando incidencia vía API: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Error en prueba de API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de cierre de incidencias...")
    
    # Probar cierre directo
    direct_success = test_close_incident()
    
    # Probar cierre vía API
    api_success = test_close_via_api()
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print(f"Cierre directo: {'✅ ÉXITO' if direct_success else '❌ FALLO'}")
    print(f"Cierre vía API: {'✅ ÉXITO' if api_success else '❌ FALLO'}")
    
    if direct_success and api_success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar los errores arriba.")
