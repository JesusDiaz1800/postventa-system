#!/usr/bin/env python
"""
Script para verificar que todas las funcionalidades del sistema estén funcionando correctamente
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.conf import settings
from apps.documents.models import Document, DocumentTemplate
from apps.ai.models import AIAnalysis, AIProvider
from apps.users.models import User
from apps.incidents.models import Incident
import logging

logger = logging.getLogger(__name__)

def check_database_models():
    """Verificar que todos los modelos de la base de datos estén funcionando"""
    print("🔍 VERIFICANDO MODELOS DE BASE DE DATOS...")
    print("=" * 50)
    
    models_status = {}
    
    try:
        # Verificar User model
        user_count = User.objects.count()
        models_status['User'] = f"✅ {user_count} usuarios"
        print(f"✅ User: {user_count} usuarios")
    except Exception as e:
        models_status['User'] = f"❌ Error: {e}"
        print(f"❌ User: Error - {e}")
    
    try:
        # Verificar Document model
        doc_count = Document.objects.count()
        models_status['Document'] = f"✅ {doc_count} documentos"
        print(f"✅ Document: {doc_count} documentos")
    except Exception as e:
        models_status['Document'] = f"❌ Error: {e}"
        print(f"❌ Document: Error - {e}")
    
    try:
        # Verificar DocumentTemplate model
        template_count = DocumentTemplate.objects.count()
        models_status['DocumentTemplate'] = f"✅ {template_count} plantillas"
        print(f"✅ DocumentTemplate: {template_count} plantillas")
    except Exception as e:
        models_status['DocumentTemplate'] = f"❌ Error: {e}"
        print(f"❌ DocumentTemplate: Error - {e}")
    
    try:
        # Verificar AIAnalysis model
        ai_count = AIAnalysis.objects.count()
        models_status['AIAnalysis'] = f"✅ {ai_count} análisis de IA"
        print(f"✅ AIAnalysis: {ai_count} análisis de IA")
    except Exception as e:
        models_status['AIAnalysis'] = f"❌ Error: {e}"
        print(f"❌ AIAnalysis: Error - {e}")
    
    try:
        # Verificar AIProvider model
        provider_count = AIProvider.objects.count()
        models_status['AIProvider'] = f"✅ {provider_count} proveedores de IA"
        print(f"✅ AIProvider: {provider_count} proveedores de IA")
    except Exception as e:
        models_status['AIProvider'] = f"❌ Error: {e}"
        print(f"❌ AIProvider: Error - {e}")
    
    try:
        # Verificar Incident model
        incident_count = Incident.objects.count()
        models_status['Incident'] = f"✅ {incident_count} incidencias"
        print(f"✅ Incident: {incident_count} incidencias")
    except Exception as e:
        models_status['Incident'] = f"❌ Error: {e}"
        print(f"❌ Incident: Error - {e}")
    
    return models_status

def check_shared_folder():
    """Verificar que la carpeta compartida esté accesible"""
    print("\n📁 VERIFICANDO CARPETA COMPARTIDA...")
    print("=" * 50)
    
    shared_folder = getattr(settings, 'SHARED_FOLDER_PATH', 'Y:\\CONTROL DE CALIDAD\\postventa')
    
    try:
        if os.path.exists(shared_folder):
            print(f"✅ Carpeta compartida existe: {shared_folder}")
            
            # Verificar subcarpetas
            subfolders = ['documents', 'templates', 'images']
            for subfolder in subfolders:
                subfolder_path = os.path.join(shared_folder, subfolder)
                if os.path.exists(subfolder_path):
                    print(f"✅ Subcarpeta {subfolder} existe")
                else:
                    print(f"⚠️  Subcarpeta {subfolder} no existe, creándola...")
                    try:
                        os.makedirs(subfolder_path, exist_ok=True)
                        print(f"✅ Subcarpeta {subfolder} creada")
                    except Exception as e:
                        print(f"❌ Error creando subcarpeta {subfolder}: {e}")
        else:
            print(f"❌ Carpeta compartida no existe: {shared_folder}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a carpeta compartida: {e}")
        return False
    
    return True

def check_ai_providers():
    """Verificar configuración de proveedores de IA"""
    print("\n🤖 VERIFICANDO PROVEEDORES DE IA...")
    print("=" * 50)
    
    try:
        providers = AIProvider.objects.all()
        if providers.exists():
            for provider in providers:
                status = "Activo" if provider.is_active else "Inactivo"
                print(f"✅ {provider.name}: {status} (Prioridad: {provider.priority})")
        else:
            print("⚠️  No hay proveedores de IA configurados")
            print("   Ejecuta: python setup_ai_providers.py")
    except Exception as e:
        print(f"❌ Error verificando proveedores de IA: {e}")

def check_document_templates():
    """Verificar plantillas de documentos"""
    print("\n📄 VERIFICANDO PLANTILLAS DE DOCUMENTOS...")
    print("=" * 50)
    
    try:
        templates = DocumentTemplate.objects.all()
        if templates.exists():
            for template in templates:
                print(f"✅ {template.name}: {template.template_type}")
        else:
            print("⚠️  No hay plantillas de documentos configuradas")
    except Exception as e:
        print(f"❌ Error verificando plantillas: {e}")

def check_settings():
    """Verificar configuración del sistema"""
    print("\n⚙️  VERIFICANDO CONFIGURACIÓN...")
    print("=" * 50)
    
    # Verificar DEBUG
    debug_status = "Activado" if settings.DEBUG else "Desactivado"
    print(f"✅ DEBUG: {debug_status}")
    
    # Verificar ALLOWED_HOSTS
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # Verificar INSTALLED_APPS
    ai_app = 'apps.ai' in settings.INSTALLED_APPS
    print(f"✅ AI App instalada: {'Sí' if ai_app else 'No'}")
    
    # Verificar SHARED_FOLDER_PATH
    shared_path = getattr(settings, 'SHARED_FOLDER_PATH', 'No configurado')
    print(f"✅ SHARED_FOLDER_PATH: {shared_path}")

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    # Verificar modelos
    models_status = check_database_models()
    
    # Verificar carpeta compartida
    folder_ok = check_shared_folder()
    
    # Verificar proveedores de IA
    check_ai_providers()
    
    # Verificar plantillas
    check_document_templates()
    
    # Verificar configuración
    check_settings()
    
    # Resumen final
    print("\n📊 RESUMEN FINAL")
    print("=" * 50)
    
    working_models = sum(1 for status in models_status.values() if status.startswith('✅'))
    total_models = len(models_status)
    
    print(f"Modelos funcionando: {working_models}/{total_models}")
    print(f"Carpeta compartida: {'✅ OK' if folder_ok else '❌ Error'}")
    
    if working_models == total_models and folder_ok:
        print("\n🎉 ¡Sistema completamente funcional!")
    else:
        print("\n⚠️  Algunos componentes necesitan atención")
        
        # Mostrar problemas específicos
        for model, status in models_status.items():
            if not status.startswith('✅'):
                print(f"   - {model}: {status}")

if __name__ == '__main__':
    main()
