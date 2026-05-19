#!/usr/bin/env python
"""
Debug del error 400 en generación de PDF
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

print("🔍 Debugging PDF generation error...")

try:
    from apps.documents.services.ultimate_pdf_generator import UltimatePDFGenerator
    print("✅ Generador importado correctamente")
    
    # Crear generador
    generator = UltimatePDFGenerator()
    print("✅ Generador creado")
    
    # Datos de prueba que podrían estar causando el error
    test_data = {
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
        'machine_data': {
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
        }
    }
    
    print("🔄 Probando generación de PDF...")
    
    # Intentar generar PDF
    try:
        pdf_buffer = generator.generate_visit_report_pdf(test_data)
        print("✅ PDF generado exitosamente")
        
        # Guardar archivo de prueba
        with open('debug_pdf_test.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = os.path.getsize('debug_pdf_test.pdf')
        print(f"📄 Archivo guardado: debug_pdf_test.pdf ({file_size} bytes)")
        
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Error general: {str(e)}")
    import traceback
    traceback.print_exc()
