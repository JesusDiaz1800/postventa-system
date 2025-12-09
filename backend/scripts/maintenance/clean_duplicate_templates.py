#!/usr/bin/env python3
"""
Script para limpiar plantillas duplicadas y mantener solo las ultra profesionales
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

def clean_duplicate_templates():
    """Limpiar plantillas duplicadas y mantener solo las ultra profesionales"""
    
    print("🧹 LIMPIANDO PLANTILLAS DUPLICADAS")
    print("=" * 50)
    
    # Directorio de plantillas
    templates_dir = os.path.join(settings.SHARED_FOLDER_PATH, 'templates')
    
    if not os.path.exists(templates_dir):
        print(f"❌ Directorio de plantillas no existe: {templates_dir}")
        return
    
    print(f"📁 Directorio de plantillas: {templates_dir}")
    
    # Plantillas a mantener (solo las ultra profesionales)
    templates_to_keep = [
        'polifusion_lab_report_ultra_professional.docx',
        'polifusion_incident_report_ultra_professional.docx',
        'polifusion_visit_report_ultra_professional.docx'
    ]
    
    # Plantillas a eliminar (todas las demás)
    templates_to_remove = [
        'polifusion_detailed_analysis.docx',
        'polifusion_incident_report.docx',
        'polifusion_incident_report_enhanced.docx',
        'polifusion_incident_report_professional.docx',
        'polifusion_lab_report.docx',
        'polifusion_lab_report_enhanced.docx',
        'polifusion_lab_report_professional.docx',
        'polifusion_photographs.docx',
        'polifusion_visit_report.docx',
        'polifusion_visit_report_enhanced.docx',
        'polifusion_visit_report_professional.docx'
    ]
    
    # Listar archivos actuales
    current_files = os.listdir(templates_dir)
    docx_files = [f for f in current_files if f.endswith('.docx')]
    
    print(f"\n📋 Archivos actuales en el directorio:")
    for file in sorted(docx_files):
        file_path = os.path.join(templates_dir, file)
        file_size = os.path.getsize(file_path)
        status = "✅ MANTENER" if file in templates_to_keep else "❌ ELIMINAR"
        print(f"   {status} {file} ({file_size:,} bytes)")
    
    # Eliminar plantillas duplicadas
    print(f"\n🗑️ ELIMINANDO PLANTILLAS DUPLICADAS:")
    removed_count = 0
    total_size_removed = 0
    
    for template in templates_to_remove:
        template_path = os.path.join(templates_dir, template)
        
        if os.path.exists(template_path):
            try:
                file_size = os.path.getsize(template_path)
                os.remove(template_path)
                removed_count += 1
                total_size_removed += file_size
                print(f"   ✅ Eliminado: {template} ({file_size:,} bytes)")
            except Exception as e:
                print(f"   ❌ Error eliminando {template}: {e}")
        else:
            print(f"   ⚠️ No encontrado: {template}")
    
    # Verificar plantillas ultra profesionales
    print(f"\n✅ VERIFICANDO PLANTILLAS ULTRA PROFESIONALES:")
    ultra_professional_count = 0
    total_size_kept = 0
    
    for template in templates_to_keep:
        template_path = os.path.join(templates_dir, template)
        
        if os.path.exists(template_path):
            file_size = os.path.getsize(template_path)
            ultra_professional_count += 1
            total_size_kept += file_size
            print(f"   ✅ Mantenido: {template} ({file_size:,} bytes)")
        else:
            print(f"   ❌ Faltante: {template}")
    
    # Resumen final
    print(f"\n📊 RESUMEN DE LIMPIEZA:")
    print(f"   🗑️ Plantillas eliminadas: {removed_count}")
    print(f"   💾 Espacio liberado: {total_size_removed:,} bytes ({total_size_removed/1024:.1f} KB)")
    print(f"   ✅ Plantillas ultra profesionales mantenidas: {ultra_professional_count}")
    print(f"   💾 Espacio ocupado por plantillas finales: {total_size_kept:,} bytes ({total_size_kept/1024:.1f} KB)")
    
    # Listar archivos finales
    final_files = os.listdir(templates_dir)
    final_docx_files = [f for f in final_files if f.endswith('.docx')]
    
    print(f"\n📋 PLANTILLAS FINALES:")
    for file in sorted(final_docx_files):
        file_path = os.path.join(templates_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"   📄 {file} ({file_size:,} bytes)")
    
    print(f"\n🎉 ¡LIMPIEZA COMPLETADA!")
    print(f"   Solo se mantienen las plantillas ultra profesionales")
    print(f"   Sistema optimizado y sin duplicados")

if __name__ == "__main__":
    try:
        clean_duplicate_templates()
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
