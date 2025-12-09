#!/usr/bin/env python3
"""
Script para simular la petición del API del frontend
"""

import os
import sys
import django
import json
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.test import RequestFactory
from apps.users.models import User
from apps.documents.views import generate_polifusion_lab_report

def test_api_request():
    """Simular la petición del API"""
    
    print("🧪 SIMULANDO PETICIÓN DEL API")
    print("=" * 60)
    
    try:
        # Crear factory para simular request
        factory = RequestFactory()
        
        # Datos que envía el frontend
        test_data = {
            'solicitante': 'POLIFUSIÓN',
            'fecha_solicitud': '2024-01-15',
            'cliente': 'POLIFUSIÓN',
            'informante': 'Yenny Valdivia Sazo',
            'diametro': '160',
            'proyecto': 'Proyecto Alameda Park',
            'ubicacion': 'Av. Libertador Bernardo O\'Higgins 4687',
            'presion': '11.8-12',
            'temperatura': 'No registrada',
            'ensayos_adicionales': 'Análisis de fractura y cristalización',
            'comentarios_detallados': 'Se recibió una muestra compuesta por un codo de 90° PP-RCT de 160mm.',
            'conclusiones_detalladas': 'El análisis de la muestra reveló que los extremos de la tubería no fueron reducidos.',
            'experto_nombre': 'CÉSAR MUNIZAGA GARRIDO'
        }
        
        print("📋 Datos de la petición:")
        for key, value in test_data.items():
            print(f"   {key}: {value}")
        
        # Crear request simulado
        request = factory.post('/api/documents/generate-polifusion-lab-report/', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # Simular usuario autenticado
        try:
            user = User.objects.get(username='admin')
            request.user = user
            print(f"✅ Usuario autenticado: {user.username}")
        except User.DoesNotExist:
            print("❌ Usuario admin no encontrado")
            return
        
        # Simular request.data
        request.data = test_data
        
        print("\n🔄 Ejecutando vista...")
        
        # Ejecutar la vista
        response = generate_polifusion_lab_report(request)
        
        print(f"📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"   Data: {response.data}")
        else:
            print(f"   Content: {response.content}")
        
        if response.status_code == 201:
            print("✅ Petición exitosa")
        else:
            print("❌ Error en la petición")
            
    except Exception as e:
        print(f"❌ Error en la simulación: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 ¡SIMULACIÓN COMPLETADA!")

if __name__ == "__main__":
    try:
        test_api_request()
    except Exception as e:
        print(f"❌ Error durante la simulación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
