#!/usr/bin/env python3
"""
Script para debuggear el problema del informe de laboratorio
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

def test_lab_report_debug():
    """Debuggear la generación de informe de laboratorio"""
    
    print("🔍 DEBUGGEANDO INFORME DE LABORATORIO")
    print("=" * 60)
    
    # 1. Verificar configuración
    print("1️⃣ CONFIGURACIÓN:")
    print(f"   📁 SHARED_FOLDER_PATH: {settings.SHARED_FOLDER_PATH}")
    print(f"   📁 Templates: {document_generator.templates_path}")
    print(f"   📁 Documents: {document_generator.documents_path}")
    
    # 2. Verificar plantillas
    print("\n2️⃣ PLANTILLAS:")
    templates_dir = document_generator.templates_path
    lab_template = os.path.join(templates_dir, 'polifusion_lab_report_enhanced.docx')
    
    if os.path.exists(lab_template):
        size = os.path.getsize(lab_template)
        print(f"   ✅ polifusion_lab_report_enhanced.docx existe ({size:,} bytes)")
    else:
        print(f"   ❌ polifusion_lab_report_enhanced.docx NO EXISTE")
        print(f"   📁 Buscando en: {templates_dir}")
        
        # Listar archivos en el directorio
        if os.path.exists(templates_dir):
            files = os.listdir(templates_dir)
            print(f"   📋 Archivos encontrados:")
            for file in files:
                if file.endswith('.docx'):
                    print(f"      - {file}")
        else:
            print(f"   ❌ Directorio de plantillas no existe")
    
    # 3. Probar generación paso a paso
    print("\n3️⃣ PRUEBA PASO A PASO:")
    
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
            'comentarios_detallados': 'Se recibió una muestra compuesta por un codo de 90° PP-RCT de 160mm.',
            'conclusiones_detalladas': 'El análisis de la muestra reveló que los extremos de la tubería no fueron reducidos.',
            'experto_nombre': 'CÉSAR MUNIZAGA GARRIDO'
        }
        
        print("   📋 Datos de prueba preparados")
        
        # Verificar si el método existe
        if hasattr(document_generator, 'generate_polifusion_lab_report'):
            print("   ✅ Método generate_polifusion_lab_report existe")
        else:
            print("   ❌ Método generate_polifusion_lab_report NO EXISTE")
            return
        
        # Verificar si el generador mejorado existe
        try:
            from apps.documents.templates_polifusion_enhanced import polifusion_enhanced_generator
            print("   ✅ polifusion_enhanced_generator importado correctamente")
        except ImportError as e:
            print(f"   ❌ Error importando polifusion_enhanced_generator: {e}")
            return
        
        # Probar generación
        print("   🔄 Generando documento...")
        result = document_generator.generate_polifusion_lab_report(test_data)
        
        if result['success']:
            print(f"   ✅ Documento generado exitosamente")
            print(f"   📄 Archivo DOCX: {result['docx_path']}")
            print(f"   📝 Plantilla usada: {result['template_used']}")
            
            # Verificar archivo
            if os.path.exists(result['docx_path']):
                docx_size = os.path.getsize(result['docx_path'])
                print(f"   ✅ DOCX existe ({docx_size:,} bytes)")
            else:
                print(f"   ❌ DOCX no encontrado")
        else:
            print(f"   ❌ Error generando documento: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"   ❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 ¡DEBUG COMPLETADO!")

if __name__ == "__main__":
    try:
        test_lab_report_debug()
    except Exception as e:
        print(f"❌ Error durante el debug: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
