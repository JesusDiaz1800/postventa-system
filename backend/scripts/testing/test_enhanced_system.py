#!/usr/bin/env python3
"""
Script para probar el sistema mejorado de documentos
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

def test_enhanced_system():
    """Probar el sistema mejorado de documentos"""
    
    print("🧪 PROBANDO SISTEMA MEJORADO DE DOCUMENTOS")
    print("=" * 60)
    
    # 1. Verificar configuración
    print("1️⃣ CONFIGURACIÓN:")
    print(f"   📁 SHARED_FOLDER_PATH: {settings.SHARED_FOLDER_PATH}")
    print(f"   📁 Templates: {document_generator.templates_path}")
    print(f"   📁 Documents: {document_generator.documents_path}")
    
    # 2. Verificar plantillas mejoradas
    print("\n2️⃣ PLANTILLAS MEJORADAS:")
    templates_dir = document_generator.templates_path
    enhanced_templates = [
        'polifusion_lab_report_enhanced.docx',
        'polifusion_incident_report_enhanced.docx',
        'polifusion_visit_report_enhanced.docx'
    ]
    
    for template in enhanced_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            size = os.path.getsize(template_path)
            print(f"   ✅ {template} ({size:,} bytes)")
        else:
            print(f"   ❌ {template} (no encontrado)")
    
    # 3. Probar generación de documento
    print("\n3️⃣ PRUEBA DE GENERACIÓN:")
    try:
        # Datos de prueba
        test_data = {
            'solicitante': 'POLIFUSIÓN',
            'fecha_solicitud': '2024-01-15',
            'cliente': 'POLIFUSIÓN',
            'informante': 'Yenny Valdivia Sazo',
            'diametro': '160',
            'proyecto': 'Proyecto Alameda Park',
            'ubicacion': 'Av. Libertador Bernardo O\'Higgins 4687',
            'presion': '11.8-12',
            'temperatura': 'No registrada',
            'ensayos_adicionales': 'Análisis de fractura y cristalización',
            'comentarios_detallados': 'Se recibió una muestra compuesta por un codo de 90° PP-RCT de 160mm, fusionado en ambos extremos a una tubería PP-RCT/FIBERGLASS S-3.2 de 160mm.',
            'conclusiones_detalladas': 'El análisis de la muestra reveló que los extremos de la tubería no fueron reducidos, y el cordón de fusión externo era irregular.',
            'experto_nombre': 'CÉSAR MUNIZAGA GARRIDO'
        }
        
        # Generar documento
        result = document_generator.generate_polifusion_lab_report(test_data)
        
        if result['success']:
            print(f"   ✅ Documento generado exitosamente")
            print(f"   📄 Archivo DOCX: {result['docx_path']}")
            print(f"   📄 Archivo PDF: {result['pdf_path']}")
            print(f"   📝 Plantilla usada: {result['template_used']}")
            
            # Verificar que los archivos existen
            if os.path.exists(result['docx_path']):
                docx_size = os.path.getsize(result['docx_path'])
                print(f"   ✅ DOCX existe ({docx_size:,} bytes)")
            else:
                print(f"   ❌ DOCX no encontrado")
                
            if os.path.exists(result['pdf_path']):
                pdf_size = os.path.getsize(result['pdf_path'])
                print(f"   ✅ PDF existe ({pdf_size:,} bytes)")
            else:
                print(f"   ❌ PDF no encontrado")
        else:
            print(f"   ❌ Error generando documento: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"   ❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Verificar URLs de acceso
    print("\n4️⃣ URLs DE ACCESO:")
    print("   🌐 Generar informe de laboratorio:")
    print("      POST /api/documents/generate-polifusion-lab-report/")
    print("   🌐 Generar informe de incidencia:")
    print("      POST /api/documents/generate-polifusion-incident-report/")
    print("   🌐 Generar reporte de visita:")
    print("      POST /api/documents/generate-polifusion-visit-report/")
    print("   📥 Descargar documento:")
    print("      GET /api/documents/{id}/download/{file_type}/")
    print("   👁️ Ver documento:")
    print("      GET /api/documents/{id}/view/{file_type}/")
    
    print("\n🎉 ¡PRUEBA COMPLETADA!")
    print("📋 Para probar desde la aplicación web:")
    print("   1. Iniciar el servidor: python manage.py runserver 0.0.0.0:8000")
    print("   2. Abrir navegador: http://localhost:3000")
    print("   3. Ir a Documentos > Crear Documento > Informe Lab Polifusión")
    print("   4. Llenar el formulario y hacer clic en 'Generar Informe'")

if __name__ == "__main__":
    try:
        test_enhanced_system()
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
