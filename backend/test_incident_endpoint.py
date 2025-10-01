#!/usr/bin/env python3
"""
Script para probar el endpoint de incidencia
"""

import requests
import json

def test_incident_endpoint():
    """Probar el endpoint de incidencia"""
    
    print("🧪 PROBANDO ENDPOINT DE INCIDENCIA")
    print("=" * 60)
    
    # URL del endpoint de prueba
    url = "http://localhost:8000/api/documents/test/generate-polifusion-incident-report/"
    
    # Datos de prueba
    test_data = {
        'proveedor': 'Proveedor ABC',
        'obra': 'Obra XYZ',
        'cliente': 'Cliente DEF',
        'fecha_deteccion': '2024-01-15',
        'descripcion_problema': 'Problema detectado en la instalación',
        'acciones_inmediatas': 'Se suspendió la instalación inmediatamente',
        'evolucion_acciones': 'Se contactó al proveedor para revisión',
        'observaciones': 'Se requiere reemplazo del material defectuoso'
    }
    
    print("📋 Datos de prueba:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n🌐 URL: {url}")
    
    try:
        print("\n🔄 Enviando petición...")
        
        # Enviar petición
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Content: {response.text}")
        
        if response.status_code == 201:
            print("✅ Petición exitosa")
        else:
            print("❌ Error en la petición")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - El servidor no está funcionando")
    except requests.exceptions.Timeout:
        print("❌ Timeout - El servidor tardó demasiado en responder")
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
    
    print("\n🎉 ¡PRUEBA COMPLETADA!")

if __name__ == "__main__":
    test_incident_endpoint()
