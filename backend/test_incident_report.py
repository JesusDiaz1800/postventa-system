#!/usr/bin/env python3
"""
Script para probar la generación de informe de incidencia
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.conf import settings
from apps.documents.document_generator import document_generator

def test_incident_report():
    """Probar la generación de informe de incidencia"""
    
    print("🧪 PROBANDO GENERACIÓN DE INFORME DE INCIDENCIA")
    print("=" * 60)
    
    try:
        # Datos de prueba para informe de incidencia
        test_data = {
            'proveedor': 'Proveedor Test',
            'obra': 'Obra Test',
            'cliente': 'Cliente Test',
            'descripcion_problema': 'Descripción del problema encontrado en la instalación',
            'acciones_inmediatas': 'Acciones tomadas inmediatamente para resolver el problema',
            'evolucion_acciones': 'Evolución y acciones posteriores realizadas',
            'observaciones': 'Observaciones finales y cierre del caso',
            'fecha_deteccion': '15/01/2024'
        }
        
        print("📋 Datos de prueba:")
        for key, value in test_data.items():
            print(f"   {key}: {value}")
        
        print("\n🔄 Generando documento...")
        
        # Generar documento
        result = document_generator.generate_polifusion_incident_report(test_data)
        
        if result['success']:
            print(f"✅ Documento generado exitosamente")
            print(f"📄 Archivo DOCX: {result['docx_path']}")
            print(f"📄 Archivo PDF: {result['pdf_path']}")
            print(f"📝 Plantilla usada: {result['template_used']}")
            
            # Verificar que los archivos existen
            if os.path.exists(result['docx_path']):
                docx_size = os.path.getsize(result['docx_path'])
                print(f"✅ DOCX existe ({docx_size:,} bytes)")
            else:
                print(f"❌ DOCX no encontrado")
                
            if result['pdf_path'] and os.path.exists(result['pdf_path']):
                pdf_size = os.path.getsize(result['pdf_path'])
                print(f"✅ PDF existe ({pdf_size:,} bytes)")
            else:
                print(f"⚠️ PDF no generado (LibreOffice no disponible)")
        else:
            print(f"❌ Error generando documento: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 ¡PRUEBA COMPLETADA!")

if __name__ == "__main__":
    try:
        test_incident_report()
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
