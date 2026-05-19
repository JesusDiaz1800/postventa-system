#!/usr/bin/env python3
"""
Script para configurar la carpeta de red compartida
y verificar que los documentos se guarden en la ubicación correcta
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

def setup_network_folder():
    """Configurar y verificar la carpeta de red compartida"""
    
    print("🔧 CONFIGURACIÓN DE CARPETA DE RED COMPARTIDA")
    print("=" * 50)
    
    # Ruta de red configurada
    network_path = r"Y:\CONTROL DE CALIDAD\postventa"
    
    print(f"📁 Ruta de red configurada: {network_path}")
    print(f"📁 Ruta actual del sistema: {settings.SHARED_FOLDER_PATH}")
    
    # Verificar si la ruta de red es accesible
    if os.path.exists(network_path):
        print("✅ La carpeta de red es accesible")
        
        # Crear estructura de carpetas en la red
        folders = [
            'documents',      # Documentos generados (Word y PDF)
            'templates',      # Plantillas Word
            'images',         # Imágenes y logos
            'incidents',      # Archivos relacionados con incidencias
            'temp',           # Archivos temporales
            'backups',        # Respaldos
            'lab_reports'     # Reportes de laboratorio específicos
        ]
        
        print("\n📂 Creando estructura de carpetas en la red...")
        for folder in folders:
            folder_path = os.path.join(network_path, folder)
            try:
                os.makedirs(folder_path, exist_ok=True)
                print(f"  ✅ {folder}/")
            except Exception as e:
                print(f"  ❌ Error creando {folder}/: {e}")
        
        # Mover plantillas existentes a la red
        local_templates = os.path.join(settings.BASE_DIR, 'shared', 'templates')
        network_templates = os.path.join(network_path, 'templates')
        
        if os.path.exists(local_templates):
            print(f"\n📄 Moviendo plantillas de {local_templates} a {network_templates}")
            for file in os.listdir(local_templates):
                if file.endswith('.docx'):
                    local_file = os.path.join(local_templates, file)
                    network_file = os.path.join(network_templates, file)
                    try:
                        import shutil
                        shutil.copy2(local_file, network_file)
                        print(f"  ✅ {file}")
                    except Exception as e:
                        print(f"  ❌ Error moviendo {file}: {e}")
        
        print(f"\n🎉 ¡Configuración completada!")
        print(f"📁 Todos los documentos se guardarán en: {network_path}")
        print(f"📁 Estructura creada:")
        for folder in folders:
            print(f"   - {network_path}\\{folder}\\")
        
        return True
        
    else:
        print("❌ La carpeta de red NO es accesible")
        print(f"   Ruta: {network_path}")
        print("\n🔧 Posibles soluciones:")
        print("   1. Verificar que la unidad Y: esté mapeada")
        print("   2. Verificar permisos de acceso a la red")
        print("   3. Verificar que el servidor de red esté disponible")
        print("   4. Contactar al administrador de red")
        
        return False

def verify_document_generator():
    """Verificar que el generador de documentos use la ruta correcta"""
    
    print("\n🔍 VERIFICACIÓN DEL GENERADOR DE DOCUMENTOS")
    print("=" * 50)
    
    from apps.documents.document_generator import document_generator
    
    print(f"📁 Ruta de plantillas: {document_generator.templates_path}")
    print(f"📁 Ruta de documentos: {document_generator.documents_path}")
    print(f"📁 Ruta temporal: {document_generator.temp_path}")
    
    # Verificar que las rutas apunten a la red
    network_path = r"Y:\CONTROL DE CALIDAD\postventa"
    
    if document_generator.templates_path.startswith(network_path):
        print("✅ El generador está configurado para usar la carpeta de red")
    else:
        print("❌ El generador NO está configurado para usar la carpeta de red")
        print("   Se está usando la carpeta local en su lugar")

if __name__ == "__main__":
    try:
        success = setup_network_folder()
        verify_document_generator()
        
        if success:
            print("\n🎉 ¡Configuración exitosa!")
            print("📋 Próximos pasos:")
            print("   1. Reiniciar el servidor Django")
            print("   2. Probar la generación de documentos")
            print("   3. Verificar que se guarden en la carpeta de red")
        else:
            print("\n❌ Configuración fallida")
            print("   Revisar la conectividad de red antes de continuar")
            
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        import traceback
        traceback.print_exc()
