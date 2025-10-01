#!/usr/bin/env python3
"""
Script para probar directamente la vista con manejo de errores
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
import traceback

def test_view_direct():
    """Probar directamente la vista"""
    
    print("🧪 PROBANDO VISTA DIRECTAMENTE")
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
        
        print("\n🔄 Ejecutando vista con manejo de errores...")
        
        try:
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
            print(f"❌ Error ejecutando la vista: {e}")
            print("📋 Traceback completo:")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error en la simulación: {e}")
        print("📋 Traceback completo:")
        traceback.print_exc()
    
    print("\n🎉 ¡PRUEBA COMPLETADA!")

if __name__ == "__main__":
    try:
        test_view_direct()
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        traceback.print_exc()
        sys.exit(1)
