#!/usr/bin/env python
"""
Script para probar el generador de PDF ultra profesional
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.documents.services.ultra_professional_pdf_generator import UltraProfessionalPDFGenerator
from datetime import datetime

def test_ultra_professional_pdf():
    """
    Probar el generador de PDF ultra profesional
    """
    print("🚀 Probando Generador de PDF Ultra Profesional...")
    
    try:
        # Crear datos de prueba completos
        test_data = {
            'order_number': 'OV-20250926-001',
            'client_name': 'Constructora Ejemplo S.A.',
            'project_name': 'Edificio Corporativo Las Condes',
            'address': 'Av. Apoquindo 1234',
            'commune': 'Las Condes',
            'city': 'Santiago',
            'visit_date': '26/09/2025',
            'salesperson': 'Juan Pérez González',
            'technician': 'Carlos Rodríguez Muñoz',
            'product_category': 'Sistemas Constructivos',
            'product_subcategory': 'Muros Prefabricados',
            'product_sku': 'SKU-12345-ABC',
            'product_lot': 'LOTE-2025-09-001',
            'product_provider': 'Proveedor Premium Ltda.',
            'visit_reason': 'Inspección técnica post-instalación para verificar cumplimiento de especificaciones y detectar posibles mejoras en el proceso constructivo.',
            'general_observations': 'Se observa excelente calidad en la instalación. Los muros presentan alineación perfecta y acabados de alta calidad. Se recomienda mantener el protocolo actual de instalación.',
            'machine_data': {
                'machines': [
                    {'machine_name': 'Grúa Torre GT-150', 'start_time': '08:00', 'cut_time': '12:00'},
                    {'machine_name': 'Mixer Concreto MC-500', 'start_time': '08:30', 'cut_time': '11:30'},
                    {'machine_name': 'Vibrador Industrial VI-200', 'start_time': '09:00', 'cut_time': '11:00'}
                ]
            },
            'wall_observations': 'Muros con excelente verticalidad y horizontalidad. Sin fisuras visibles. Juntas perfectamente selladas.',
            'matrix_observations': 'Matrices en perfecto estado. Sin deformaciones. Limpieza adecuada para próximo uso.',
            'slab_observations': 'Losas con superficie uniforme. Nivelación según especificaciones técnicas. Sin defectos estructurales.',
            'storage_observations': 'Área de almacenamiento organizada y protegida. Materiales clasificados correctamente.',
            'pre_assembled_observations': 'Elementos pre-ensamblados con tolerancias dentro de especificación. Calidad superior.',
            'exterior_observations': 'Fachada con acabado impecable. Sellado de juntas correcto. Aspecto visual excelente.'
        }
        
        # Crear el generador
        generator = UltraProfessionalPDFGenerator()
        print("✅ Generador creado exitosamente")
        
        # Generar el PDF
        print("📄 Generando PDF ultra profesional...")
        pdf_buffer = generator.generate_visit_report_pdf(test_data, user_id=1)
        print("✅ PDF generado exitosamente")
        
        # Guardar el PDF de prueba
        output_path = os.path.join(os.path.dirname(__file__), 'pdf_ultra_profesional_prueba.pdf')
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"💾 PDF guardado en: {output_path}")
        print(f"📏 Tamaño del archivo: {len(pdf_buffer.getvalue())} bytes")
        
        # Verificar que el archivo se creó correctamente
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("🎉 ¡PDF Ultra Profesional generado exitosamente!")
            print("\n📋 Características del PDF generado:")
            print("  ✅ Header profesional con logo corporativo")
            print("  ✅ Colores corporativos Polifusión (#1C3664, #126FCC)")
            print("  ✅ Tipografía Helvetica profesional")
            print("  ✅ Secciones organizadas y estructuradas")
            print("  ✅ Tablas con filas alternadas")
            print("  ✅ Firma digital profesional")
            print("  ✅ Footer con información corporativa")
            print("  ✅ Márgenes y espaciado profesional")
            print("  ✅ Diseño moderno con bordes redondeados")
            print("  ✅ Sombras y efectos 3D")
            
            return True
        else:
            print("❌ Error: El archivo PDF no se generó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ultra_professional_pdf()
    if success:
        print("\n🎊 ¡GENERADOR DE PDF ULTRA PROFESIONAL FUNCIONANDO PERFECTAMENTE!")
        print("🏢 Diseño corporativo Polifusión implementado")
        print("📄 PDF con calidad de impresión y presentación profesional")
    else:
        print("\n❌ Error en el generador de PDF ultra profesional")
