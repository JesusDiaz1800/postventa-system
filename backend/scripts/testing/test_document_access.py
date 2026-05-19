#!/usr/bin/env python3
"""
Script para probar el acceso a documentos desde la aplicación
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
from apps.documents.models import Document
from apps.documents.document_generator import document_generator

def test_document_access():
    """Probar el acceso a documentos"""
    
    print("🔍 PRUEBA DE ACCESO A DOCUMENTOS")
    print("=" * 50)
    
    # 1. Verificar configuración
    print("1️⃣ CONFIGURACIÓN:")
    print(f"   📁 SHARED_FOLDER_PATH: {settings.SHARED_FOLDER_PATH}")
    print(f"   📁 Documents path: {document_generator.documents_path}")
    print(f"   📁 Templates path: {document_generator.templates_path}")
    
    # 2. Verificar documentos existentes
    print("\n2️⃣ DOCUMENTOS EN BASE DE DATOS:")
    documents = Document.objects.all()
    print(f"   📄 Total de documentos: {documents.count()}")
    
    for doc in documents[:5]:  # Mostrar solo los primeros 5
        print(f"   📄 ID: {doc.id} - {doc.title}")
        print(f"      DOCX: {doc.docx_path} ({'✅' if os.path.exists(doc.docx_path) else '❌'})")
        print(f"      PDF:  {doc.pdf_path} ({'✅' if os.path.exists(doc.pdf_path) else '❌'})")
    
    # 3. Verificar estructura de carpetas
    print("\n3️⃣ ESTRUCTURA DE CARPETAS:")
    network_path = r"Y:\CONTROL DE CALIDAD\postventa"
    
    folders = ['documents', 'templates', 'images', 'incidents', 'temp', 'backups', 'lab_reports']
    for folder in folders:
        folder_path = os.path.join(network_path, folder)
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            print(f"   ✅ {folder}/ ({len(files)} archivos)")
        else:
            print(f"   ❌ {folder}/ (no existe)")
    
    # 4. Verificar plantillas
    print("\n4️⃣ PLANTILLAS DISPONIBLES:")
    templates_path = os.path.join(network_path, 'templates')
    if os.path.exists(templates_path):
        templates = [f for f in os.listdir(templates_path) if f.endswith('.docx')]
        for template in templates:
            template_path = os.path.join(templates_path, template)
            size = os.path.getsize(template_path)
            print(f"   ✅ {template} ({size:,} bytes)")
    else:
        print("   ❌ Carpeta de plantillas no encontrada")
    
    # 5. Verificar documentos generados
    print("\n5️⃣ DOCUMENTOS GENERADOS:")
    documents_path = os.path.join(network_path, 'documents')
    if os.path.exists(documents_path):
        files = os.listdir(documents_path)
        docx_files = [f for f in files if f.endswith('.docx')]
        pdf_files = [f for f in files if f.endswith('.pdf')]
        print(f"   📄 Archivos DOCX: {len(docx_files)}")
        print(f"   📄 Archivos PDF: {len(pdf_files)}")
        
        for file in files[:5]:  # Mostrar solo los primeros 5
            file_path = os.path.join(documents_path, file)
            size = os.path.getsize(file_path)
            print(f"   📄 {file} ({size:,} bytes)")
    else:
        print("   ❌ Carpeta de documentos no encontrada")
    
    # 6. URLs de acceso
    print("\n6️⃣ URLs DE ACCESO:")
    print("   🌐 Ver PDF en navegador:")
    print("      GET /api/documents/{id}/view/pdf/")
    print("   📥 Descargar PDF:")
    print("      GET /api/documents/{id}/download/pdf/")
    print("   📥 Descargar Word:")
    print("      GET /api/documents/{id}/download/docx/")
    print("   ℹ️  Información del documento:")
    print("      GET /api/documents/{id}/info/")
    
    print("\n🎉 ¡Prueba completada!")
    print("📋 Para probar desde la aplicación:")
    print("   1. Iniciar el servidor Django")
    print("   2. Generar un documento")
    print("   3. Ir a la página de documentos")
    print("   4. Hacer clic en los botones de ver/descargar")

if __name__ == "__main__":
    try:
        test_document_access()
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
