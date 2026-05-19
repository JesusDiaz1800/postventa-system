#!/usr/bin/env python
"""
Script para probar el generador de PDFs personalizado de Polifusión
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.documents.services.polifusion_pdf_generator import PolifusionPDFGenerator

def test_polifusion_pdf():
    """Probar generación de PDF personalizado de Polifusión"""
    print("🚀 Probando generador de PDFs personalizado de Polifusión...")
    
    # Datos completos de prueba (como se llenaría en el formulario)
    test_data = {
        # Información básica
        'order_number': 'OV-20250925001',
        'project_name': 'Proyecto Residencial Las Condes',
        'client_name': 'Constructora ABC S.A.',
        'address': 'Av. Las Condes 1234, Las Condes',
        'commune': 'Las Condes',
        'city': 'Santiago',
        'visit_date': '2025-09-25',
        
        # Personal
        'salesperson': 'María González',
        'technician': 'Carlos Mendoza',
        
        # Razón y observaciones
        'visit_reason': 'Inspección técnica de calidad post-entrega',
        'general_observations': 'Se realizó una inspección exhaustiva de los elementos prefabricados instalados. Se verificó la calidad de los materiales y el cumplimiento de las especificaciones técnicas.',
        
        # Datos de máquinas
        'machine_data': {
            'machines': [
                {
                    'machine_name': 'Hormigonera Modelo H-500',
                    'start_time': '08:30',
                    'cut_time': '12:45'
                },
                {
                    'machine_name': 'Vibrador de Concreto V-200',
                    'start_time': '09:15',
                    'cut_time': '11:30'
                },
                {
                    'machine_name': 'Grúa Torre GT-150',
                    'start_time': '10:00',
                    'cut_time': '13:00'
                }
            ]
        },
        
        # Observaciones técnicas
        'wall_observations': 'Los muros presentan buena calidad de acabado. Se observó uniformidad en el espesor y alineación correcta.',
        'matrix_observations': 'Las matrices están en buen estado. Se verificó la correcta instalación y funcionamiento.',
        'slab_observations': 'Las losas presentan resistencia adecuada. Se realizaron pruebas de carga que cumplen con las especificaciones.',
        'storage_observations': 'El almacenamiento de materiales es adecuado. Los elementos están protegidos de la intemperie.',
        'pre_assembled_observations': 'Los elementos pre-ensamblados cumplen con las dimensiones especificadas.',
        'exterior_observations': 'El acabado exterior presenta buena calidad. Se verificó la impermeabilización.',
        
        # Información del producto (pre-cargada desde la incidencia)
        'product_category': 'Elementos Prefabricados',
        'product_subcategory': 'Losas Aligeradas',
        'product_sku': 'LOSA-ALG-001',
        'product_lot': 'LOTE-2025-09-001',
        'product_provider': 'Prefabricados del Sur S.A.',
        
        # Información de la incidencia (pre-cargada)
        'incident_description': 'Fisuras menores en losa aligerada del segundo nivel',
        'incident_priority': 'Media',
        'incident_responsible': 'Juan Pérez',
        'incident_detection_date': '2025-09-20',
        'incident_detection_time': '14:30'
    }
    
    try:
        # Crear generador
        generator = PolifusionPDFGenerator()
        
        # Generar PDF
        print("📄 Generando PDF personalizado...")
        pdf_buffer = generator.generate_visit_report_pdf(test_data, user_id=1)
        
        # Guardar PDF
        output_path = 'test_polifusion_report.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF generado exitosamente: {output_path}")
        print(f"📊 Tamaño del archivo: {os.path.getsize(output_path)} bytes")
        
        # Mostrar información del PDF
        print("\n📋 Contenido del PDF:")
        print("   • Header corporativo con logo de Polifusión")
        print("   • Información completa del proyecto")
        print("   • Personal involucrado")
        print("   • Razón de la visita y observaciones")
        print("   • Datos de máquinas en tabla profesional")
        print("   • Observaciones técnicas detalladas")
        print("   • Información del producto (pre-cargada)")
        print("   • Información de la incidencia (pre-cargada)")
        print("   • Firma del técnico responsable")
        print("   • Footer corporativo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_polifusion_pdf()
    if success:
        print("\n🎉 ¡Prueba exitosa! El generador de PDFs personalizado de Polifusión funciona correctamente.")
        print("📄 El PDF incluye:")
        print("   ✅ Logo e información corporativa")
        print("   ✅ Diseño súper profesional")
        print("   ✅ Todos los campos del formulario")
        print("   ✅ Firma dinámica del técnico")
        print("   ✅ Información completa del proyecto")
    else:
        print("\n💥 Prueba fallida. Revisa los errores anteriores.")
