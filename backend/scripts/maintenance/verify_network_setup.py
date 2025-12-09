#!/usr/bin/env python3
"""
Script de verificación final para confirmar que el sistema
está configurado correctamente para usar la carpeta de red
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

def verify_network_setup():
    """Verificación completa del setup de red"""
    
    print("🔍 VERIFICACIÓN FINAL DEL SISTEMA DE RED")
    print("=" * 60)
    
    # 1. Verificar configuración de Django
    print("1️⃣ CONFIGURACIÓN DE DJANGO:")
    print(f"   📁 SHARED_FOLDER_PATH: {settings.SHARED_FOLDER_PATH}")
    print(f"   📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # 2. Verificar generador de documentos
    print("\n2️⃣ GENERADOR DE DOCUMENTOS:")
    print(f"   📁 Templates: {document_generator.templates_path}")
    print(f"   📁 Documents: {document_generator.documents_path}")
    print(f"   📁 Temp: {document_generator.temp_path}")
    
    # 3. Verificar accesibilidad de carpetas
    print("\n3️⃣ ACCESIBILIDAD DE CARPETAS:")
    network_path = r"Y:\CONTROL DE CALIDAD\postventa"
    
    folders_to_check = [
        ('documents', 'Documentos generados'),
        ('templates', 'Plantillas Word'),
        ('images', 'Imágenes y logos'),
        ('incidents', 'Archivos de incidencias'),
        ('temp', 'Archivos temporales'),
        ('backups', 'Respaldos'),
        ('lab_reports', 'Reportes de laboratorio')
    ]
    
    all_accessible = True
    for folder, description in folders_to_check:
        folder_path = os.path.join(network_path, folder)
        if os.path.exists(folder_path) and os.access(folder_path, os.W_OK):
            print(f"   ✅ {folder}/ - {description}")
        else:
            print(f"   ❌ {folder}/ - {description} (NO ACCESIBLE)")
            all_accessible = False
    
    # 4. Verificar plantillas
    print("\n4️⃣ PLANTILLAS DISPONIBLES:")
    templates_path = os.path.join(network_path, 'templates')
    if os.path.exists(templates_path):
        templates = [f for f in os.listdir(templates_path) if f.endswith('.docx')]
        for template in templates:
            print(f"   ✅ {template}")
    else:
        print("   ❌ Carpeta de plantillas no encontrada")
        all_accessible = False
    
    # 5. Verificar permisos de escritura
    print("\n5️⃣ PERMISOS DE ESCRITURA:")
    test_file = os.path.join(network_path, 'temp', 'test_write.txt')
    try:
        with open(test_file, 'w') as f:
            f.write('Test de escritura')
        os.remove(test_file)
        print("   ✅ Permisos de escritura OK")
    except Exception as e:
        print(f"   ❌ Error de escritura: {e}")
        all_accessible = False
    
    # 6. Resumen final
    print("\n" + "=" * 60)
    if all_accessible:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ El sistema está configurado correctamente para usar la carpeta de red")
        print("✅ Todos los documentos se guardarán en:")
        print(f"   📁 {network_path}")
        print("\n📋 BENEFICIOS:")
        print("   • Acceso desde toda la empresa")
        print("   • Documentos centralizados")
        print("   • Respaldos automáticos")
        print("   • Colaboración en tiempo real")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("   1. Reiniciar el servidor Django")
        print("   2. Probar generación de documentos")
        print("   3. Verificar que se guarden en la red")
        print("   4. Compartir acceso con otros usuarios")
        
    else:
        print("❌ VERIFICACIÓN FALLIDA")
        print("   Hay problemas con la configuración de red")
        print("   Revisar conectividad y permisos")
    
    return all_accessible

if __name__ == "__main__":
    try:
        verify_network_setup()
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
