#!/usr/bin/env python
"""
Test de la API de generación de PDF
"""

import requests
import json

# URL base del servidor
BASE_URL = "http://localhost:8000/api"

# Datos de login
login_data = {
    "username": "admin",
    "password": "admin123"
}

# Datos del reporte de visita
report_data = {
    'order_number': 'OV-20250926-001',
    'client_name': 'Constructora San José S.A.',
    'project_name': 'Edificio Residencial Las Flores',
    'address': 'Av. Las Flores 1234, Las Condes',
    'commune': 'Las Condes',
    'city': 'Santiago',
    'visit_date': '26/09/2025',
    'salesperson': 'Juan Pérez',
    'technician': 'Carlos Rodríguez',
    'product_category': 'Tubería de Polietileno',
    'product_subcategory': 'PE-100',
    'product_sku': 'PE-100-25',
    'product_lot': 'LOTE-2025-001',
    'product_provider': 'Polietileno Chile S.A.',
    'visit_reason': 'Inspección de calidad de materiales entregados',
    'general_observations': 'Se realizó una inspección exhaustiva de los materiales entregados para el proyecto Edificio Residencial Las Flores. Se verificó la calidad de las tuberías y se confirmó que cumplen con los estándares requeridos según norma NCh 2205.',
    'wall_observations': 'Las paredes presentan buen estado general, sin fisuras visibles. Se verificó la adherencia del material.',
    'matrix_observations': 'La matriz de PE-100 muestra uniformidad en el espesor. Medición con calibre digital confirma espesor nominal.',
    'slab_observations': 'La losa presenta buen acabado superficial. No se observan defectos de superficie.',
    'storage_observations': 'Los materiales están almacenados correctamente en ambiente controlado. Temperatura y humedad dentro de rangos normales.',
    'pre_assembled_observations': 'Los elementos pre-ensamblados están en buen estado. Verificación de soldaduras sin defectos.',
    'exterior_observations': 'El exterior del edificio presenta buen acabado. No se observan problemas de estanqueidad.',
    'machine_data': json.dumps({
        'machines': [
            {
                'machine_name': 'Extrusora Principal',
                'start_time': '08:00',
                'cut_time': '16:30'
            },
            {
                'machine_name': 'Extrusora Secundaria',
                'start_time': '09:15',
                'cut_time': '17:00'
            }
        ]
    }),
    'related_incident_id': '78'  # ID de una incidencia sin reporte de visita
}

def test_pdf_generation():
    """Probar la generación de PDF a través de la API"""
    
    print("🔍 Probando generación de PDF a través de la API...")
    
    try:
        # 1. Login para obtener token
        print("1. Iniciando sesión...")
        login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json().get('access')
        if not token:
            print("❌ No se obtuvo token de acceso")
            return
        
        print("✅ Login exitoso")
        
        # 2. Generar PDF
        print("2. Generando PDF...")
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        pdf_response = requests.post(
            f"{BASE_URL}/documents/pdf/visit-report/", 
            json=report_data,
            headers=headers
        )
        
        print(f"Status Code: {pdf_response.status_code}")
        
        if pdf_response.status_code == 200:
            print("✅ PDF generado exitosamente")
            
            # Guardar PDF
            with open('test_api_pdf.pdf', 'wb') as f:
                f.write(pdf_response.content)
            
            file_size = len(pdf_response.content)
            print(f"📄 PDF guardado: test_api_pdf.pdf ({file_size} bytes)")
            
        else:
            print(f"❌ Error generando PDF: {pdf_response.status_code}")
            print(f"Response: {pdf_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
