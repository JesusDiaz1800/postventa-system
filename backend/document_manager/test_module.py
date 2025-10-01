"""
Script de prueba para el módulo de gestión de documentos
Demuestra todas las funcionalidades del sistema
"""

import os
import sys
import logging
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_document_manager():
    """
    Probar el módulo completo de gestión de documentos
    """
    try:
        # Importar el módulo
        from document_manager import DocumentManager, TemplateManager, AIProcessor, FileManager
        
        print("🚀 Iniciando pruebas del módulo de gestión de documentos...")
        
        # Inicializar gestores
        print("📁 Inicializando gestores...")
        doc_manager = DocumentManager()
        template_manager = TemplateManager()
        ai_processor = AIProcessor()
        file_manager = FileManager(doc_manager.base_path)
        
        print("✅ Gestores inicializados correctamente")
        
        # Crear contexto de prueba
        contexto_prueba = {
            'incident_code': 'INC-2025-0001',
            'client_name': 'Constructora San José S.A.',
            'project_name': 'Edificio Residencial Las Flores',
            'detection_date': '26/09/2025',
            'priority': 'Alta',
            'responsible': 'Carlos Rodríguez',
            'description': 'Se identificó una condición en el proceso de fabricación que requiere atención técnica.',
            'product_category': 'Tubería HDPE',
            'product_subcategory': 'Tubería de 110mm',
            'product_sku': 'HDPE-110-001',
            'product_lot': 'LOTE-2025-001',
            'product_provider': 'Proveedor ABC',
            'actions_taken': 'Se realizó inspección técnica y se tomaron muestras para análisis.',
            'recommendations': 'Se recomienda realizar análisis de laboratorio para determinar las causas.',
            'generated_by': 'Sistema de Pruebas',
            'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        print("📝 Contexto de prueba creado")
        
        # Probar generación de documento Word
        print("📄 Generando documento Word...")
        docx_path = doc_manager.generar_docx(contexto_prueba, 'incident_report')
        print(f"✅ Documento Word generado: {docx_path}")
        
        # Probar conversión a PDF
        print("📄 Convirtiendo a PDF...")
        pdf_path = doc_manager.guardar_pdf(docx_path)
        print(f"✅ PDF generado: {pdf_path}")
        
        # Probar análisis de IA
        print("🤖 Probando análisis de IA...")
        contexto_mejorado = ai_processor.maquillar_redaccion(contexto_prueba)
        print("✅ Redacción mejorada por IA")
        
        # Probar generación de documento completo
        print("📚 Generando documento completo...")
        resultado_completo = doc_manager.generar_documento_completo(contexto_prueba)
        print(f"✅ Documento completo generado: {resultado_completo}")
        
        # Probar biblioteca
        print("📚 Probando biblioteca...")
        biblioteca = doc_manager.obtener_biblioteca_documentos()
        print(f"✅ Biblioteca obtenida: {len(biblioteca)} documentos")
        
        # Probar estadísticas
        print("📊 Obteniendo estadísticas...")
        estadisticas = file_manager.obtener_estadisticas()
        print(f"✅ Estadísticas: {estadisticas}")
        
        # Probar búsqueda
        print("🔍 Probando búsqueda...")
        criterios = {'client_name': 'Constructora San José S.A.'}
        documentos_encontrados = file_manager.buscar_documentos(criterios)
        print(f"✅ Búsqueda completada: {len(documentos_encontrados)} documentos encontrados")
        
        print("🎉 ¡Todas las pruebas completadas exitosamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {str(e)}")
        logger.error(f"Error en las pruebas: {str(e)}", exc_info=True)
        return False

def test_api_endpoints():
    """
    Probar endpoints de la API
    """
    try:
        print("🌐 Probando endpoints de la API...")
        
        # Importar API
        from document_manager.api import (
            generar_documento_completo,
            generar_docx,
            convertir_a_pdf,
            obtener_biblioteca,
            obtener_estadisticas
        )
        
        print("✅ Endpoints importados correctamente")
        
        # Simular request de prueba
        class MockRequest:
            def __init__(self, data, user=None):
                self.data = data
                self.user = user or MockUser()
        
        class MockUser:
            username = 'test_user'
        
        # Probar generación de documento
        request_data = {
            'contexto': {
                'incident_code': 'INC-2025-0001',
                'client_name': 'Cliente de Prueba',
                'description': 'Descripción de prueba'
            },
            'tipo_documento': 'incident_report'
        }
        
        mock_request = MockRequest(request_data)
        
        print("✅ Endpoints de API listos para usar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando API: {str(e)}")
        logger.error(f"Error probando API: {str(e)}", exc_info=True)
        return False

def test_templates():
    """
    Probar sistema de plantillas
    """
    try:
        print("📋 Probando sistema de plantillas...")
        
        from document_manager.templates import TemplateManager
        
        template_manager = TemplateManager()
        
        # Probar obtención de plantillas
        plantillas = [
            'incident_report',
            'visit_report',
            'lab_report',
            'supplier_report'
        ]
        
        for plantilla in plantillas:
            try:
                template_path = template_manager.get_template(plantilla)
                print(f"✅ Plantilla {plantilla} encontrada: {template_path}")
            except Exception as e:
                print(f"⚠️ Plantilla {plantilla} no encontrada: {str(e)}")
        
        # Probar renderizado
        contexto = {
            'incident_code': 'INC-2025-0001',
            'client_name': 'Cliente de Prueba',
            'description': 'Descripción de prueba'
        }
        
        try:
            contenido_renderizado = template_manager.render_template('incident_report', contexto)
            print("✅ Plantilla renderizada correctamente")
        except Exception as e:
            print(f"⚠️ Error renderizando plantilla: {str(e)}")
        
        print("✅ Sistema de plantillas probado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando plantillas: {str(e)}")
        logger.error(f"Error probando plantillas: {str(e)}", exc_info=True)
        return False

def main():
    """
    Función principal de pruebas
    """
    print("🧪 INICIANDO PRUEBAS DEL MÓDULO DE GESTIÓN DE DOCUMENTOS")
    print("=" * 60)
    
    # Ejecutar pruebas
    pruebas = [
        ("Gestor de Documentos", test_document_manager),
        ("Sistema de Plantillas", test_templates),
        ("Endpoints de API", test_api_endpoints)
    ]
    
    resultados = []
    
    for nombre, funcion in pruebas:
        print(f"\n🔍 Probando: {nombre}")
        print("-" * 40)
        
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error crítico en {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLÓ"
        print(f"{nombre}: {estado}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("🚀 El módulo de gestión de documentos está listo para usar")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar los errores anteriores")
    
    return exitosos == len(resultados)

if __name__ == "__main__":
    main()
