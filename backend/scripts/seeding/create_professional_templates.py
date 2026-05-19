#!/usr/bin/env python3
"""
Script para crear plantillas profesionales de Polifusión
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
from apps.documents.templates_professional import ProfessionalTemplateGenerator

def create_professional_templates():
    """Crear plantillas profesionales"""
    
    print("🎨 CREANDO PLANTILLAS PROFESIONALES DE POLIFUSIÓN")
    print("=" * 60)
    
    # Verificar directorio de plantillas
    templates_dir = os.path.join(settings.SHARED_FOLDER_PATH, 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    print(f"📁 Directorio de plantillas: {templates_dir}")
    
    # Crear generador
    generator = ProfessionalTemplateGenerator()
    
    # Crear plantillas profesionales
    templates_to_create = [
        {
            'name': 'Informe de Laboratorio Profesional',
            'filename': 'polifusion_lab_report_professional.docx',
            'method': generator.create_professional_lab_report
        },
        {
            'name': 'Informe de Incidencia Profesional',
            'filename': 'polifusion_incident_report_professional.docx',
            'method': generator.create_professional_incident_report
        },
        {
            'name': 'Reporte de Visita Profesional',
            'filename': 'polifusion_visit_report_professional.docx',
            'method': generator.create_professional_visit_report
        }
    ]
    
    for template in templates_to_create:
        print(f"\n🔄 Creando {template['name']}...")
        
        template_path = os.path.join(templates_dir, template['filename'])
        
        try:
            template['method'](template_path)
            
            # Verificar que se creó
            if os.path.exists(template_path):
                file_size = os.path.getsize(template_path)
                print(f"   ✅ Creado exitosamente: {template['filename']} ({file_size:,} bytes)")
            else:
                print(f"   ❌ Error: No se pudo crear {template['filename']}")
                
        except Exception as e:
            print(f"   ❌ Error creando {template['name']}: {e}")
    
    print(f"\n🎉 ¡PLANTILLAS PROFESIONALES CREADAS!")
    print(f"📁 Ubicación: {templates_dir}")
    
    # Listar archivos creados
    print(f"\n📋 Archivos creados:")
    for file in os.listdir(templates_dir):
        if file.endswith('.docx'):
            file_path = os.path.join(templates_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   📄 {file} ({file_size:,} bytes)")

if __name__ == "__main__":
    try:
        create_professional_templates()
    except Exception as e:
        print(f"❌ Error durante la creación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
