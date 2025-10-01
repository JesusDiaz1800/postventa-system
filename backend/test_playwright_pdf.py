#!/usr/bin/env python
"""
Script para probar el generador de PDFs con Playwright
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.documents.services.playwright_pdf_generator import PlaywrightPDFGenerator

def test_playwright_pdf():
    """Probar generación de PDF con Playwright"""
    print("🚀 Probando generador de PDFs con Playwright...")
    
    # Datos de prueba
    test_data = {
        'order_number': 'OV-20250925001',
        'project_name': 'Proyecto de Prueba',
        'client_name': 'Cliente de Prueba',
        'address': 'Dirección de Prueba 123',
        'commune': 'Lampa',
        'city': 'Santiago',
        'visit_date': '2025-09-25',
        'salesperson': 'Vendedor de Prueba',
        'technician': 'Técnico de Prueba',
        'visit_reason': 'Inspección técnica de calidad',
        'general_observations': 'Observaciones generales del proyecto',
        'machine_data': {
            'machines': [
                {
                    'machine_name': 'Máquina 1',
                    'start_time': '08:00',
                    'cut_time': '12:00'
                },
                {
                    'machine_name': 'Máquina 2',
                    'start_time': '09:00',
                    'cut_time': '13:00'
                }
            ]
        },
        'wall_observations': 'Observaciones de muro',
        'matrix_observations': 'Observaciones de matriz',
        'slab_observations': 'Observaciones de losa',
        'storage_observations': 'Observaciones de almacenamiento',
        'pre_assembled_observations': 'Observaciones de pre-ensamblado',
        'exterior_observations': 'Observaciones de exterior'
    }
    
    try:
        # Crear generador
        generator = PlaywrightPDFGenerator()
        
        # Generar PDF
        print("📄 Generando PDF...")
        pdf_buffer = generator.generate_visit_report_pdf(test_data)
        
        # Guardar PDF
        output_path = 'test_playwright_report.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF generado exitosamente: {output_path}")
        print(f"📊 Tamaño del archivo: {os.path.getsize(output_path)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_playwright_pdf()
    if success:
        print("\n🎉 ¡Prueba exitosa! El generador de PDFs con Playwright funciona correctamente.")
    else:
        print("\n💥 Prueba fallida. Revisa los errores anteriores.")
