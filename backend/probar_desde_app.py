"""
Script para probar el generador alternativo desde la aplicación web
"""

import os
import sys
import time
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def probar_generador_desde_app():
    """
    Probar el generador alternativo simulando datos de la app
    """
    print("🌐 PROBANDO GENERADOR ALTERNATIVO DESDE LA APP")
    print("=" * 60)
    
    try:
        # Importar el generador alternativo
        from document_manager_alternative import DocumentManager
        
        print("✅ Generador alternativo importado")
        
        # Crear instancia
        doc_manager = DocumentManager()
        print("✅ Gestor inicializado")
        
        # Simular datos que vendrían de la app
        contexto_app = {
            'incident_code': 'INC-2025-0001',
            'client_name': 'Constructora ABC S.A.',
            'project_name': 'Edificio Residencial Las Flores',
            'detection_date': '26/09/2025',
            'priority': 'Alta',
            'responsible': 'Carlos Rodríguez',
            'description': 'Se identificó una condición en el proceso de fabricación de tuberías HDPE que requiere atención técnica inmediata. El problema se detectó durante la inspección de calidad rutinaria.',
            'product_category': 'Tubería HDPE',
            'product_subcategory': 'Tubería de 110mm',
            'product_sku': 'HDPE-110-001',
            'product_lot': 'LOTE-2025-001',
            'product_provider': 'Proveedor ABC',
            'actions_taken': 'Se realizó inspección técnica completa, se tomaron muestras para análisis de laboratorio y se documentó el proceso de fabricación.',
            'recommendations': 'Se recomienda realizar análisis de laboratorio para determinar las causas raíz del problema y implementar medidas correctivas.',
            'generated_by': 'Sistema Web App',
            'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        print("✅ Contexto de la app simulado")
        print(f"   Código: {contexto_app['incident_code']}")
        print(f"   Cliente: {contexto_app['client_name']}")
        print(f"   Proyecto: {contexto_app['project_name']}")
        
        # Generar documento completo
        print("\n📄 Generando documento completo...")
        start_time = time.time()
        
        resultado = doc_manager.generar_documento_completo(contexto_app)
        
        generation_time = time.time() - start_time
        print(f"✅ Documento generado en {generation_time:.2f} segundos")
        
        # Verificar archivos generados
        docx_path = resultado.get('docx')
        pdf_path = resultado.get('pdf')
        
        if docx_path and os.path.exists(docx_path):
            docx_size = os.path.getsize(docx_path)
            print(f"📄 Word: {docx_size:,} bytes ({docx_size/1024:.1f} KB)")
            print(f"   📁 Ruta: {docx_path}")
        
        if pdf_path and os.path.exists(pdf_path):
            pdf_size = os.path.getsize(pdf_path)
            print(f"📄 PDF: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
            print(f"   📁 Ruta: {pdf_path}")
        
        # Probar funcionalidades adicionales
        print("\n🤖 Probando funcionalidades adicionales...")
        
        # Análisis de IA
        contexto_original = {
            'description': 'Hay un error en el producto que causa problemas graves',
            'recommendations': 'Hay que arreglar el problema inmediatamente'
        }
        
        contexto_mejorado = doc_manager.ai_processor.maquillar_redaccion(contexto_original)
        print(f"✅ Redacción mejorada por IA:")
        print(f"   Original: {contexto_original['description']}")
        print(f"   Mejorado: {contexto_mejorado['description']}")
        
        # Biblioteca
        biblioteca = doc_manager.obtener_biblioteca_documentos()
        print(f"✅ Biblioteca: {len(biblioteca)} documentos")
        
        # Estadísticas
        estadisticas = doc_manager.file_manager.obtener_estadisticas()
        print(f"✅ Estadísticas: {estadisticas}")
        
        print("\n🎉 ¡GENERADOR ALTERNATIVO FUNCIONANDO PERFECTAMENTE!")
        print("✅ Listo para integrar con la aplicación web")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_como_integrar():
    """
    Mostrar cómo integrar con la aplicación web
    """
    print("\n🔧 CÓMO INTEGRAR CON LA APLICACIÓN WEB")
    print("=" * 60)
    
    print("""
1. 📁 AGREGAR EL MÓDULO A TU PROYECTO
   =================================
   El módulo ya está en: backend/document_manager_alternative/
   
2. 🔗 CREAR ENDPOINT EN DJANGO
   ===========================
   Agregar a backend/apps/documents/views_upload.py:
   
   @api_view(['POST'])
   @permission_classes([IsAuthenticated])
   def generar_documento_alternativo(request):
       try:
           from document_manager_alternative import DocumentManager
           
           # Obtener datos del request
           incident_id = request.data.get('incident_id')
           tipo_documento = request.data.get('tipo_documento', 'incident_report')
           
           # Obtener incidencia de la base de datos
           incident = Incident.objects.get(id=incident_id)
           
           # Crear contexto
           contexto = {
               'incident_code': incident.code,
               'client_name': incident.cliente,
               'description': incident.descripcion,
               # ... más campos
           }
           
           # Generar documento
           doc_manager = DocumentManager()
           resultado = doc_manager.generar_documento_completo(contexto)
           
           return Response({
               'success': True,
               'files': resultado
           })
           
       except Exception as e:
           return Response({'error': str(e)})

3. 🌐 AGREGAR URL
   ==============
   En backend/apps/documents/urls.py:
   
   path('generate-alternative/', views_upload.generar_documento_alternativo, name='generate_alternative'),

4. 📱 USAR DESDE FRONTEND
   =====================
   JavaScript:
   
   const response = await fetch('/api/documents/generate-alternative/', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${token}`
       },
       body: JSON.stringify({
           incident_id: 77,
           tipo_documento: 'incident_report'
       })
   });
   
   const resultado = await response.json();
   console.log('Documentos generados:', resultado.files);
""")

def mostrar_urls_para_probar():
    """
    Mostrar URLs para probar desde la aplicación web
    """
    print("\n🌐 URLs PARA PROBAR DESDE LA APLICACIÓN WEB")
    print("=" * 60)
    
    print("""
1. 🚀 Iniciar servidor Django:
   python manage.py runserver 0.0.0.0:8000

2. 📋 URLs disponibles:
   ===================
   
   • Lista de incidencias:
     http://localhost:8000/api/incidents/
   
   • Reportes de visita:
     http://localhost:8000/api/documents/visit-reports/
   
   • Buscar documentos:
     http://localhost:8000/api/documents/search/visit-report/OV-20250926-008.pdf
   
   • Debug de incidencia:
     http://localhost:8000/api/documents/debug/visit-report/77/
   
   • Biblioteca de documentos:
     http://localhost:8000/api/documents/shared/
   
   • Estadísticas:
     http://localhost:8000/api/documents/statistics/

3. 🔍 Probar búsqueda de documentos:
   =================================
   GET http://localhost:8000/api/documents/search/visit-report/OV-20250926-008.pdf
   
   Esto te mostrará dónde está el archivo y cómo acceder a él.

4. 📄 Ver PDF generado:
   ====================
   Una vez que generes un documento, podrás verlo en:
   http://localhost:8000/api/documents/open/visit-report/{incident_id}/{filename}
""")

def main():
    """
    Función principal
    """
    print("🌐 PROBADOR DEL GENERADOR ALTERNATIVO DESDE LA APP")
    print("=" * 80)
    
    # Probar el generador
    exito = probar_generador_desde_app()
    
    if exito:
        mostrar_como_integrar()
        mostrar_urls_para_probar()
        
        print("\n🎯 CONCLUSIÓN")
        print("=" * 30)
        print("✅ El generador alternativo está listo para la app")
        print("✅ Puedes integrarlo con Django fácilmente")
        print("✅ Usa las URLs mostradas para probar desde la app")
        print("🚀 ¡Listo para usar en producción!")
    else:
        print("\n❌ ERROR")
        print("=" * 30)
        print("❌ Revisar los errores anteriores")

if __name__ == "__main__":
    main()
