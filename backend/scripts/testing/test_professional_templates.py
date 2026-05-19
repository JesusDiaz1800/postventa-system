#!/usr/bin/env python3
"""
Script para probar las nuevas plantillas profesionales
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

def test_professional_templates():
    """Probar las nuevas plantillas profesionales"""
    
    print("🎨 PROBANDO PLANTILLAS PROFESIONALES")
    print("=" * 60)
    
    # 1. Probar informe de laboratorio profesional
    print("\n1️⃣ PROBANDO INFORME DE LABORATORIO PROFESIONAL")
    lab_data = {
        'solicitante': 'POLIFUSIÓN S.A.',
        'fecha_solicitud': '2024-01-15',
        'cliente': 'Cliente Corporativo',
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
    
    result = document_generator.generate_polifusion_lab_report(lab_data)
    
    if result['success']:
        print(f"   ✅ Informe de laboratorio profesional generado")
        print(f"   📄 Archivo: {result['filename']}")
        print(f"   📁 Ruta: {result['docx_path']}")
        print(f"   🎨 Plantilla: {result['template_used']}")
        
        # Verificar archivo
        if os.path.exists(result['docx_path']):
            file_size = os.path.getsize(result['docx_path'])
            print(f"   📏 Tamaño: {file_size:,} bytes")
        else:
            print(f"   ❌ Archivo no encontrado")
    else:
        print(f"   ❌ Error: {result.get('error', 'Error desconocido')}")
    
    # 2. Probar informe de incidencia profesional
    print("\n2️⃣ PROBANDO INFORME DE INCIDENCIA PROFESIONAL")
    incident_data = {
        'proveedor': 'Proveedor Corporativo',
        'obra': 'Obra Industrial',
        'cliente': 'Cliente Empresarial',
        'fecha_deteccion': '2024-01-15',
        'descripcion_problema': 'Problema detectado en la instalación de tuberías',
        'acciones_inmediatas': 'Se suspendió la instalación inmediatamente',
        'evolucion_acciones': 'Se contactó al proveedor para revisión técnica',
        'observaciones': 'Se requiere reemplazo del material defectuoso'
    }
    
    result = document_generator.generate_polifusion_incident_report(incident_data)
    
    if result['success']:
        print(f"   ✅ Informe de incidencia profesional generado")
        print(f"   📄 Archivo: {result['filename']}")
        print(f"   📁 Ruta: {result['docx_path']}")
        print(f"   🎨 Plantilla: {result['template_used']}")
        
        # Verificar archivo
        if os.path.exists(result['docx_path']):
            file_size = os.path.getsize(result['docx_path'])
            print(f"   📏 Tamaño: {file_size:,} bytes")
        else:
            print(f"   ❌ Archivo no encontrado")
    else:
        print(f"   ❌ Error: {result.get('error', 'Error desconocido')}")
    
    # 3. Probar reporte de visita profesional
    print("\n3️⃣ PROBANDO REPORTE DE VISITA PROFESIONAL")
    visit_data = {
        'obra': 'Obra de Prueba Profesional',
        'cliente': 'Cliente de Prueba Profesional',
        'vendedor': 'Vendedor Profesional',
        'tecnico': 'Técnico Profesional',
        'fecha_visita': '2024-01-15',
        'personal_info': 'Personal técnico especializado presente',
        'roles_contactos': 'Roles y contactos identificados correctamente',
        'maquinaria_uso': 'Uso de maquinaria observado y documentado',
        'observaciones_instalacion': 'Instalación realizada según estándares',
        'observaciones_material': 'Material en excelente estado',
        'observaciones_tecnico': 'Aspectos técnicos cumplidos',
        'observaciones_general': 'Visita exitosa y productiva',
        'firma_vendedor': 'Firma del vendedor',
        'firma_tecnico': 'Firma del técnico'
    }
    
    result = document_generator.generate_polifusion_visit_report(visit_data)
    
    if result['success']:
        print(f"   ✅ Reporte de visita profesional generado")
        print(f"   📄 Archivo: {result['filename']}")
        print(f"   📁 Ruta: {result['docx_path']}")
        print(f"   🎨 Plantilla: {result['template_used']}")
        
        # Verificar archivo
        if os.path.exists(result['docx_path']):
            file_size = os.path.getsize(result['docx_path'])
            print(f"   📏 Tamaño: {file_size:,} bytes")
        else:
            print(f"   ❌ Archivo no encontrado")
    else:
        print(f"   ❌ Error: {result.get('error', 'Error desconocido')}")
    
    print(f"\n🎉 ¡PRUEBA DE PLANTILLAS PROFESIONALES COMPLETADA!")
    
    # Listar archivos generados
    documents_dir = os.path.join(settings.SHARED_FOLDER_PATH, 'documents')
    if os.path.exists(documents_dir):
        files = os.listdir(documents_dir)
        recent_files = [f for f in files if f.endswith('.docx') and 'PROFESIONAL' in f.upper()]
        
        if recent_files:
            print(f"\n📋 Archivos profesionales generados:")
            for file in recent_files[-3:]:  # Últimos 3 archivos
                file_path = os.path.join(documents_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   📄 {file} ({file_size:,} bytes)")

if __name__ == "__main__":
    try:
        test_professional_templates()
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
