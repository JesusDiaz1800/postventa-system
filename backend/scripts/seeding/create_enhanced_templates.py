#!/usr/bin/env python3
"""
Script para crear las plantillas mejoradas de Polifusión
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
from apps.documents.templates_polifusion_enhanced import polifusion_enhanced_generator

def create_enhanced_templates():
    """Crear plantillas mejoradas de Polifusión"""
    
    print("🎨 CREANDO PLANTILLAS MEJORADAS DE POLIFUSIÓN")
    print("=" * 60)
    
    # Ruta de plantillas
    templates_dir = os.path.join(settings.SHARED_FOLDER_PATH, 'templates')
    
    if not os.path.exists(templates_dir):
        print(f"❌ Error: La carpeta de plantillas no existe: {templates_dir}")
        return False
    
    print(f"📁 Carpeta de plantillas: {templates_dir}")
    
    try:
        # 1. Crear plantilla de informe de laboratorio mejorada
        lab_template_path = os.path.join(templates_dir, 'polifusion_lab_report_enhanced.docx')
        polifusion_enhanced_generator.create_lab_report_template(lab_template_path)
        print(f"✅ Creada plantilla mejorada: {os.path.basename(lab_template_path)}")
        
        # 2. Crear plantilla de informe de incidencia mejorada
        incident_template_path = os.path.join(templates_dir, 'polifusion_incident_report_enhanced.docx')
        polifusion_enhanced_generator.create_incident_report_template(incident_template_path)
        print(f"✅ Creada plantilla mejorada: {os.path.basename(incident_template_path)}")
        
        # 3. Crear plantilla de reporte de visita mejorada
        visit_template_path = os.path.join(templates_dir, 'polifusion_visit_report_enhanced.docx')
        polifusion_enhanced_generator.create_visit_report_template(visit_template_path)
        print(f"✅ Creada plantilla mejorada: {os.path.basename(visit_template_path)}")
        
        print("\n🎉 ¡TODAS LAS PLANTILLAS MEJORADAS CREADAS EXITOSAMENTE!")
        print("\n📋 Características de las plantillas mejoradas:")
        print("   🎨 Diseño profesional con colores corporativos")
        print("   🏢 Logo de Polifusión integrado")
        print("   📊 Tablas estructuradas y bien formateadas")
        print("   🎯 Secciones claramente definidas")
        print("   📝 Contenido técnico detallado")
        print("   ✨ Elementos visuales mejorados")
        
        print("\n🚀 Próximos pasos:")
        print("   1. Reiniciar el servidor Django")
        print("   2. Probar la generación de documentos")
        print("   3. Verificar el diseño en los archivos generados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando plantillas mejoradas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = create_enhanced_templates()
        if success:
            print("\n✅ Proceso completado exitosamente")
        else:
            print("\n❌ Proceso falló")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
