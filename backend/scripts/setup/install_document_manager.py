"""
Script de instalación y configuración del módulo de gestión de documentos
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_dependencies():
    """
    Instalar dependencias del módulo
    """
    try:
        print("📦 Instalando dependencias...")
        
        # Ruta del archivo requirements
        requirements_path = os.path.join(os.path.dirname(__file__), 'document_manager', 'requirements.txt')
        
        if not os.path.exists(requirements_path):
            print("❌ Archivo requirements.txt no encontrado")
            return False
        
        # Instalar dependencias
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', requirements_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print(f"❌ Error instalando dependencias: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error en instalación: {str(e)}")
        return False

def create_directories():
    """
    Crear directorios necesarios
    """
    try:
        print("📁 Creando directorios...")
        
        # Directorios base
        base_path = os.path.join(os.getcwd(), 'documents')
        directories = [
            base_path,
            os.path.join(base_path, 'templates'),
            os.path.join(base_path, 'output'),
            os.path.join(base_path, 'temp'),
            os.path.join(base_path, 'library'),
            os.path.join(base_path, 'shared'),
            os.path.join(base_path, 'library', 'incidents'),
            os.path.join(base_path, 'library', 'visit_reports'),
            os.path.join(base_path, 'library', 'lab_reports'),
            os.path.join(base_path, 'library', 'supplier_reports'),
            os.path.join(base_path, 'shared', 'incidents'),
            os.path.join(base_path, 'shared', 'visit_reports'),
            os.path.join(base_path, 'shared', 'lab_reports'),
            os.path.join(base_path, 'shared', 'supplier_reports')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Directorio creado: {directory}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando directorios: {str(e)}")
        return False

def configure_django():
    """
    Configurar integración con Django
    """
    try:
        print("🔧 Configurando integración con Django...")
        
        # Verificar si existe settings.py
        settings_path = os.path.join(os.path.dirname(__file__), 'postventa_system', 'settings.py')
        
        if not os.path.exists(settings_path):
            print("⚠️ Archivo settings.py no encontrado, saltando configuración Django")
            return True
        
        # Leer settings actual
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings_content = f.read()
        
        # Verificar si ya está configurado
        if 'document_manager' in settings_content:
            print("✅ document_manager ya está en INSTALLED_APPS")
            return True
        
        # Agregar document_manager a INSTALLED_APPS
        if 'INSTALLED_APPS' in settings_content:
            # Buscar la línea de INSTALLED_APPS y agregar document_manager
            lines = settings_content.split('\n')
            new_lines = []
            
            for line in lines:
                new_lines.append(line)
                if 'INSTALLED_APPS' in line and '=' in line:
                    # Agregar document_manager después de la línea de INSTALLED_APPS
                    new_lines.append("    'document_manager',")
            
            # Escribir archivo actualizado
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print("✅ document_manager agregado a INSTALLED_APPS")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando Django: {str(e)}")
        return False

def create_urls_config():
    """
    Crear configuración de URLs
    """
    try:
        print("🔗 Configurando URLs...")
        
        # Crear archivo urls.py para document_manager
        urls_content = '''
"""
URLs para el módulo de gestión de documentos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

app_name = 'document_manager'

urlpatterns = [
    # Generación de documentos
    path('generate/', generar_documento_completo, name='generate_document'),
    path('generate-docx/', generar_docx, name='generate_docx'),
    path('convert-pdf/', convertir_a_pdf, name='convert_pdf'),
    path('insert-image/', insertar_imagen, name='insert_image'),
    
    # Análisis con IA
    path('analyze-images/', analizar_imagenes, name='analyze_images'),
    
    # Biblioteca de documentos
    path('library/', obtener_biblioteca, name='get_library'),
    path('library/stats/', obtener_estadisticas, name='get_stats'),
    path('library/search/', buscar_documentos, name='search_documents'),
    path('library/export/', exportar_biblioteca, name='export_library'),
    path('library/import/', importar_biblioteca, name='import_library'),
    
    # Descarga de documentos
    path('download/<str:tipo>/<str:filename>/', descargar_documento, name='download_document'),
]
'''
        
        urls_path = os.path.join(os.path.dirname(__file__), 'document_manager', 'urls.py')
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(urls_content)
        
        print("✅ URLs configuradas")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando URLs: {str(e)}")
        return False

def test_installation():
    """
    Probar la instalación
    """
    try:
        print("🧪 Probando instalación...")
        
        # Importar módulo
        sys.path.append(os.path.dirname(__file__))
        from document_manager import DocumentManager
        
        # Crear instancia
        doc_manager = DocumentManager()
        print("✅ DocumentManager inicializado correctamente")
        
        # Probar generación de plantillas
        template_manager = doc_manager.template_manager
        print("✅ TemplateManager inicializado correctamente")
        
        # Probar gestor de archivos
        file_manager = doc_manager.file_manager
        print("✅ FileManager inicializado correctamente")
        
        print("✅ Instalación probada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error probando instalación: {str(e)}")
        return False

def main():
    """
    Función principal de instalación
    """
    print("🚀 INSTALADOR DEL MÓDULO DE GESTIÓN DE DOCUMENTOS")
    print("=" * 60)
    
    # Pasos de instalación
    pasos = [
        ("Instalando dependencias", install_dependencies),
        ("Creando directorios", create_directories),
        ("Configurando Django", configure_django),
        ("Configurando URLs", create_urls_config),
        ("Probando instalación", test_installation)
    ]
    
    exitosos = 0
    
    for nombre, funcion in pasos:
        print(f"\n🔧 {nombre}...")
        try:
            if funcion():
                print(f"✅ {nombre} completado")
                exitosos += 1
            else:
                print(f"❌ {nombre} falló")
        except Exception as e:
            print(f"❌ Error en {nombre}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE INSTALACIÓN")
    print("=" * 60)
    
    if exitosos == len(pasos):
        print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
        print("\n📖 Próximos pasos:")
        print("1. Ejecutar: python document_manager/test_module.py")
        print("2. Configurar variables de entorno (opcional)")
        print("3. Integrar URLs en tu proyecto Django")
        print("4. ¡Comenzar a usar el módulo!")
        
        print("\n🔗 URLs disponibles:")
        print("- /api/documents/generate/")
        print("- /api/documents/library/")
        print("- /api/documents/download/<tipo>/<filename>/")
        
    else:
        print(f"⚠️ Instalación parcial: {exitosos}/{len(pasos)} pasos completados")
        print("Revisar los errores anteriores y reintentar")
    
    return exitosos == len(pasos)

if __name__ == "__main__":
    main()
