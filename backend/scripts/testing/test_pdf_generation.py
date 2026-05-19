#!/usr/bin/env python
"""
Script de prueba para verificar la generación de PDFs
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.documents.services.pdf_generator import ProfessionalPDFGenerator

def test_visit_report_pdf():
    """Probar generación de PDF de reporte de visita"""
    print("🧪 Probando generación de PDF de reporte de visita...")
    
    # Datos de prueba
    test_data = {
        'report_number': 'RV-2025-001',
        'order_number': 'OV-20250924-001',
        'visit_date': '2025-09-24',
        'technician': 'Juan Pérez',
        'client_name': 'Constructora ABC S.A.',
        'project_name': 'Edificio Residencial Las Flores',
        'address': 'Av. Principal 123, Santiago',
        'commune': 'Las Condes',
        'city': 'Santiago',
        'construction_company': 'Constructora ABC S.A.',
        'salesperson': 'María González',
        'installer': 'Carlos López',
        'installer_phone': '+56 9 1234 5678',
        'visit_reason': '01-Visita Técnica',
        'product_category': 'Tubería BETA',
        'product_subcategory': 'Fuga',
        'product_sku': 'TUB-001',
        'product_lot': 'L2025001',
        'product_provider': 'Polifusion S.A.',
        'incident_description': 'Fuga en tubería principal de agua potable en el sótano del edificio',
        'machine_data': {
            'machines': [
                {'machine': 'Máquina 1', 'start': '08:00', 'cut': '12:00'},
                {'machine': 'Máquina 2', 'start': '13:00', 'cut': '17:00'}
            ]
        }
    }
    
    try:
        # Crear generador
        pdf_generator = ProfessionalPDFGenerator()
        
        # Generar PDF
        pdf_buffer = pdf_generator.generate_visit_report_pdf(test_data)
        
        # Guardar PDF de prueba
        output_path = 'test_visit_report.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF generado exitosamente: {output_path}")
        print(f"📄 Tamaño del archivo: {len(pdf_buffer.getvalue())} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_quality_report_pdf():
    """Probar generación de PDF de reporte de calidad"""
    print("\n🧪 Probando generación de PDF de reporte de calidad...")
    
    # Datos de prueba
    test_data = {
        'report_number': 'QR-2025-001',
        'report_date': '2025-09-24',
        'inspection_date': '2025-09-24',
        'inspection_location': 'Planta de Producción',
        'follow_up_responsible': 'Ana Martínez',
        'product_sku': 'TUB-001',
        'product_lot': 'L2025001',
        'product_category': 'Tubería BETA',
        'product_subcategory': 'Fuga',
        'product_description': 'Tubería principal de agua potable',
        'supplier_name': 'Polifusion S.A.',
        'inspection_scope': 'Análisis de calidad del producto TUB-001 del lote L2025001',
        'inspection_criteria': 'Normas ISO 9001, especificaciones técnicas del producto y requisitos del cliente',
        'sampling_method': 'Muestreo aleatorio según ISO 2859-1',
        'sample_size': '10 unidades del lote reportado',
        'visual_inspection': 'Inspección visual detallada del producto para identificar defectos superficiales',
        'dimensional_analysis': 'Medición de dimensiones críticas según especificaciones técnicas',
        'mechanical_tests': 'Pruebas de resistencia y durabilidad según normativas aplicables',
        'chemical_analysis': 'Análisis de composición química y propiedades del material',
        'other_tests': 'Pruebas adicionales según requerimientos específicos del producto',
        'conclusions': 'El producto cumple con las especificaciones técnicas establecidas',
        'recommendations': 'Continuar con el proceso de producción bajo las mismas condiciones'
    }
    
    try:
        # Crear generador
        pdf_generator = ProfessionalPDFGenerator()
        
        # Generar PDF
        pdf_buffer = pdf_generator.generate_quality_report_pdf(test_data)
        
        # Guardar PDF de prueba
        output_path = 'test_quality_report.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF generado exitosamente: {output_path}")
        print(f"📄 Tamaño del archivo: {len(pdf_buffer.getvalue())} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de generación de PDFs...")
    
    # Probar reporte de visita
    visit_success = test_visit_report_pdf()
    
    # Probar reporte de calidad
    quality_success = test_quality_report_pdf()
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print(f"Reporte de Visita: {'✅ ÉXITO' if visit_success else '❌ FALLO'}")
    print(f"Reporte de Calidad: {'✅ ÉXITO' if quality_success else '❌ FALLO'}")
    
    if visit_success and quality_success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar los errores arriba.")