#!/usr/bin/env python
"""
Test del generador de PDF ultimate profesional
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
    from apps.documents.services.ultimate_professional_pdf_generator import UltimateProfessionalPDFGenerator
    print("✅ Importación exitosa del generador PDF ultimate")
    
    # Crear generador
    generator = UltimateProfessionalPDFGenerator()
    print("✅ Generador ultimate creado")
    
    # Datos de prueba completos
    test_data = {
        'order_number': 'OV-20250926-001',
        'client_name': 'Empresa Constructora ABC',
        'project_name': 'Edificio Residencial Las Flores',
        'address': 'Av. Principal 1234',
        'commune': 'Las Condes',
        'city': 'Santiago',
        'visit_date': '26/09/2025',
        'salesperson': 'Juan Pérez',
        'technician': 'Carlos Rodríguez',
        'product_category': 'Polietileno',
        'product_subcategory': 'Tubería',
        'product_sku': 'PE-100-25',
        'product_lot': 'LOTE-2025-001',
        'product_provider': 'Proveedor XYZ',
        'visit_reason': 'Inspección de calidad de materiales',
        'general_observations': 'Se realizó una inspección exhaustiva de los materiales entregados. Se verificó la calidad de las tuberías y se confirmó que cumplen con los estándares requeridos.',
        'wall_observations': 'Las paredes presentan buen estado general, sin fisuras visibles.',
        'matrix_observations': 'La matriz de polietileno muestra uniformidad en el espesor.',
        'slab_observations': 'La losa presenta buen acabado superficial.',
        'storage_observations': 'Los materiales están almacenados correctamente.',
        'pre_assembled_observations': 'Los elementos pre-ensamblados están en buen estado.',
        'exterior_observations': 'El exterior del edificio presenta buen acabado.',
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
    with open('test_ultimate_pdf_output.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    file_size = os.path.getsize('test_ultimate_pdf_output.pdf')
    print(f"🎉 ¡PDF ultimate profesional generado exitosamente!")
    print(f"📄 Archivo: test_ultimate_pdf_output.pdf")
    print(f"📏 Tamaño: {file_size} bytes")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
