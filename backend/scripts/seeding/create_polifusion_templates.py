#!/usr/bin/env python3
"""
Script para crear las plantillas de Polifusión
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.documents.templates_polifusion import polifusion_generator

def create_templates():
    """Crear todas las plantillas de Polifusión"""
    
    # Crear directorio de plantillas si no existe
    templates_dir = os.path.join(os.path.dirname(__file__), 'shared', 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    print("🔧 Creando plantillas de Polifusión...")
    
    try:
        # Crear plantilla de informe de laboratorio
        lab_report_path = os.path.join(templates_dir, 'polifusion_lab_report.docx')
        polifusion_generator.create_lab_report_template(lab_report_path)
        print(f"✅ Creada plantilla: {lab_report_path}")
        
        # Crear plantilla de fotografías
        photos_path = os.path.join(templates_dir, 'polifusion_photographs.docx')
        polifusion_generator.create_photographs_template(photos_path)
        print(f"✅ Creada plantilla: {photos_path}")
        
        # Crear plantilla de análisis detallado
        analysis_path = os.path.join(templates_dir, 'polifusion_detailed_analysis.docx')
        polifusion_generator.create_detailed_analysis_template(analysis_path)
        print(f"✅ Creada plantilla: {analysis_path}")
        
        # Crear plantilla de informe de incidencia
        incident_path = os.path.join(templates_dir, 'polifusion_incident_report.docx')
        polifusion_generator.create_incident_report_template(incident_path)
        print(f"✅ Creada plantilla: {incident_path}")
        
        # Crear plantilla de reporte de visita
        visit_path = os.path.join(templates_dir, 'polifusion_visit_report.docx')
        polifusion_generator.create_visit_report_template(visit_path)
        print(f"✅ Creada plantilla: {visit_path}")
        
        print("\n🎉 ¡Todas las plantillas de Polifusión han sido creadas exitosamente!")
        print(f"📁 Ubicación: {templates_dir}")
        
    except Exception as e:
        print(f"❌ Error creando plantillas: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = create_templates()
    sys.exit(0 if success else 1)
