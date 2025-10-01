#!/usr/bin/env python3
"""
Script para probar el endpoint de prueba
"""

import requests
import json

def test_endpoint():
    """Probar el endpoint de prueba"""
    
    print("🧪 PROBANDO ENDPOINT DE PRUEBA")
    print("=" * 60)
    
    # URL del endpoint de prueba
    url = "http://localhost:8000/api/documents/test/generate-polifusion-lab-report/"
    
    # Datos de prueba
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
    test_endpoint()
