#!/usr/bin/env python
"""
Test del nuevo generador de PDF ultimate profesional
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

print("📧 Modo desarrollo: Los emails se mostrarán en la consola")
print("✅ Django configurado correctamente")

try:
    from apps.documents.services.ultimate_pdf_generator import UltimatePDFGenerator
    print("✅ Importación exitosa del generador PDF ultimate")
    
    # Crear generador
    generator = UltimatePDFGenerator()
    print("✅ Generador ultimate creado")
    
    # Datos de prueba completos
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
    
    # Generar PDF ultimate
    print("🔄 Generando PDF ultimate profesional...")
    pdf_buffer = generator.generate_visit_report_pdf(test_data)
    print("✅ PDF ultimate generado")
    
    # Guardar archivo de prueba
    with open('test_ultimate_pdf_new.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    file_size = os.path.getsize('test_ultimate_pdf_new.pdf')
    print(f"🎉 ¡PDF ultimate profesional generado exitosamente!")
    print(f"📄 Archivo: test_ultimate_pdf_new.pdf")
    print(f"📏 Tamaño: {file_size} bytes")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
