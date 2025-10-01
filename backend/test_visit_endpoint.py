#!/usr/bin/env python3
"""
Script para probar el endpoint de visita
"""

import requests
import json

def test_visit_endpoint():
    """Probar el endpoint de visita"""
    
    print("🧪 PROBANDO ENDPOINT DE VISITA")
    print("=" * 60)
    
    # URL del endpoint de prueba
    url = "http://localhost:8000/api/documents/test/generate-polifusion-visit-report/"
    
    # Datos de prueba
    test_data = {
        'obra': 'Obra de Prueba',
        'cliente': 'Cliente de Prueba',
        'vendedor': 'Vendedor de Prueba',
        'tecnico': 'Técnico de Prueba',
        'fecha_visita': '2024-01-15',
        'personal_info': 'Información del personal presente',
        'roles_contactos': 'Roles y contactos identificados',
        'maquinaria_uso': 'Uso de maquinaria observado',
        'observaciones_instalacion': 'Observaciones sobre la instalación',
        'observaciones_material': 'Observaciones sobre el material',
        'observaciones_tecnico': 'Observaciones técnicas',
        'observaciones_general': 'Observaciones generales',
        'firma_vendedor': 'Firma del vendedor',
        'firma_tecnico': 'Firma del técnico'
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
    test_visit_endpoint()
