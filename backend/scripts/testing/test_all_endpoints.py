#!/usr/bin/env python
"""
Script para verificar que todos los endpoints estén funcionando correctamente
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_auth_token():
    """Obtener token de autenticación para las pruebas"""
    try:
        # Crear o obtener usuario de prueba
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@polifusion.cl',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'admin'
            }
        )
        
        # Generar token
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    except Exception as e:
        print(f"Error obteniendo token: {e}")
        return None

def test_endpoint(method, url, data=None, headers=None, expected_status=200):
    """Probar un endpoint específico"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        status_ok = response.status_code == expected_status
        print(f"{'✅' if status_ok else '❌'} {method} {url} - Status: {response.status_code}")
        
        if not status_ok:
            print(f"   Error: {response.text[:200]}")
        
        return status_ok
    except Exception as e:
        print(f"❌ {method} {url} - Error: {e}")
        return False

def main():
    """Función principal para probar todos los endpoints"""
    print("🔍 VERIFICANDO TODOS LOS ENDPOINTS...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    token = get_auth_token()
    
    if not token:
        print("❌ No se pudo obtener token de autenticación")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Lista de endpoints a probar
    endpoints = [
        # Auth endpoints
        ('GET', '/api/auth/user/', None, headers, 200),
        
        # Documents endpoints
        ('GET', '/api/documents/', None, headers, 200),
        ('GET', '/api/documents/real-files/', None, headers, 200),
        ('GET', '/api/documents/real-files/stats/', None, headers, 200),
        
        # AI endpoints
        ('GET', '/api/ai/providers/status/', None, headers, 200),
        ('GET', '/api/ai/analyses/', None, headers, 200),
        ('GET', '/api/ai/dashboard-stats/', None, headers, 200),
        
        # Reports endpoints
        ('GET', '/api/reports/dashboard/', None, headers, 200),
        
        # Test PDF generation
        ('POST', '/api/documents/generate-polifusion-lab-report-pdf/', {
            'solicitante': 'Test',
            'cliente': 'Cliente Test',
            'proyecto': 'Proyecto Test',
            'experto_nombre': 'Experto Test',
            'fecha_solicitud': '2024-01-01',
            'diametro': '160',
            'ubicacion': 'Ubicación Test',
            'presion': '10',
            'temperatura': '25',
            'informante': 'Informante Test',
            'ensayos_adicionales': 'Ensayos test',
            'comentarios_detallados': 'Comentarios test',
            'conclusiones_detalladas': 'Conclusiones test',
            'analisis_detallado': 'Análisis test'
        }, headers, 201),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for method, url, data, headers, expected_status in endpoints:
        full_url = base_url + url
        if test_endpoint(method, full_url, data, headers, expected_status):
            passed += 1
    
    print("=" * 50)
    print(f"📊 RESULTADOS: {passed}/{total} endpoints funcionando correctamente")
    
    if passed == total:
        print("🎉 ¡Todos los endpoints están funcionando correctamente!")
    else:
        print(f"⚠️  {total - passed} endpoints necesitan atención")
    
    # Probar endpoints sin autenticación
    print("\n🔓 PROBANDO ENDPOINTS SIN AUTENTICACIÓN...")
    print("=" * 50)
    
    public_endpoints = [
        ('GET', '/api/documents/test/generate-polifusion-lab-report/', None, {'Content-Type': 'application/json'}, 405),  # POST required
    ]
    
    for method, url, data, headers, expected_status in public_endpoints:
        full_url = base_url + url
        test_endpoint(method, full_url, data, headers, expected_status)

if __name__ == '__main__':
    main()
