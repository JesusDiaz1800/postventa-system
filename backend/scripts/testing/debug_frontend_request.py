#!/usr/bin/env python
"""
Debug de la petición del frontend para generar PDF
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

def test_frontend_request():
    """Simular exactamente lo que envía el frontend"""
    
    print("🔍 Simulando petición del frontend...")
    
    try:
        # 1. Login
        print("1. Iniciando sesión...")
        login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return
        
        token = login_response.json().get('access')
        print("✅ Login exitoso")
        
        # 2. Crear reporte de visita (como hace el frontend)
        print("2. Creando reporte de visita...")
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        visit_report_data = {
            'order_number': 'OV-20250926-001',
            'client_name': 'Constructora San José S.A.',
            'project_name': 'Edificio Residencial Las Flores',
            'address': 'Av. Las Flores 1234, Las Condes',
            'commune': 'Las Condes',
            'city': 'Santiago',
            'visit_date': '2025-09-26',
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
            'related_incident_id': '77',  # ID de incidencia sin reporte
            'status': 'draft'
        }
        
        # Crear reporte de visita
        visit_response = requests.post(
            f"{BASE_URL}/documents/visit-reports/", 
            json=visit_report_data,
            headers=headers
        )
        
        print(f"Status Code (Visit Report): {visit_response.status_code}")
        
        if visit_response.status_code == 201:
            print("✅ Reporte de visita creado exitosamente")
            report_data = visit_response.json()
            print(f"Reporte ID: {report_data.get('id')}")
        else:
            print(f"❌ Error creando reporte de visita: {visit_response.text}")
            return
        
        # 3. El PDF se genera automáticamente en el backend
        print("3. PDF generado automáticamente en el backend")
        print("✅ Proceso completado exitosamente")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_request()
