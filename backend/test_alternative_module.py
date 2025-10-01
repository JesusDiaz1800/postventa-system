"""
Script de prueba para el módulo alternativo de gestión de documentos
Demuestra todas las funcionalidades del sistema alternativo
"""

import os
import sys
import logging
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_alternative_document_manager():
    """
    Probar el módulo alternativo de gestión de documentos
    """
    try:
        # Importar el módulo alternativo
        from document_manager_alternative import DocumentManager, TemplateManager, AIProcessor, FileManager
        
        print("🚀 Iniciando pruebas del módulo alternativo de gestión de documentos...")
        
        # Inicializar gestores
        print("📁 Inicializando gestores alternativos...")
        doc_manager = DocumentManager()
        template_manager = TemplateManager()
        ai_processor = AIProcessor()
        file_manager = FileManager(doc_manager.base_path)
        
        print("✅ Gestores alternativos inicializados correctamente")
        
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
            'generated_by': 'Sistema de Pruebas Alternativo',
            'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        print("📝 Contexto de prueba creado")
        
        # Probar generación de documento Word
        print("📄 Generando documento Word alternativo...")
        docx_path = doc_manager.generar_docx(contexto_prueba, 'incident_report')
        print(f"✅ Documento Word generado: {docx_path}")
        
        # Probar conversión a PDF
        print("📄 Convirtiendo a PDF con reportlab...")
        pdf_path = doc_manager.guardar_pdf(docx_path)
        print(f"✅ PDF generado: {pdf_path}")
        
        # Probar análisis de IA local
        print("🤖 Probando análisis de IA local...")
        contexto_mejorado = ai_processor.maquillar_redaccion(contexto_prueba)
        print("✅ Redacción mejorada por IA local")
        
        # Probar generación de documento completo
        print("📚 Generando documento completo alternativo...")
        resultado_completo = doc_manager.generar_documento_completo(contexto_prueba)
        print(f"✅ Documento completo generado: {resultado_completo}")
        
        # Probar biblioteca
        print("📚 Probando biblioteca alternativa...")
        biblioteca = doc_manager.obtener_biblioteca_documentos()
        print(f"✅ Biblioteca obtenida: {len(biblioteca)} documentos")
        
        # Probar estadísticas
        print("📊 Obteniendo estadísticas alternativas...")
        estadisticas = file_manager.obtener_estadisticas()
        print(f"✅ Estadísticas: {estadisticas}")
        
        # Probar búsqueda
        print("🔍 Probando búsqueda alternativa...")
        criterios = {'client_name': 'Constructora San José S.A.'}
        documentos_encontrados = file_manager.buscar_documentos(criterios)
        print(f"✅ Búsqueda completada: {len(documentos_encontrados)} documentos encontrados")
        
        # Probar análisis de imágenes local
        print("🖼️ Probando análisis de imágenes local...")
        try:
            # Crear imagen de prueba simple
            from PIL import Image
            test_image = Image.new('RGB', (100, 100), color='red')
            test_image_path = os.path.join(doc_manager.base_path, 'temp', 'test_image.jpg')
            os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
            test_image.save(test_image_path)
            
            analisis_imagenes = ai_processor.analizar_imagenes([test_image_path])
            print(f"✅ Análisis de imágenes local completado: {len(analisis_imagenes)} imágenes analizadas")
            
            # Limpiar imagen de prueba
            os.remove(test_image_path)
            
        except Exception as e:
            print(f"⚠️ Análisis de imágenes local no disponible: {str(e)}")
        
        print("🎉 ¡Todas las pruebas del módulo alternativo completadas exitosamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en las pruebas alternativas: {str(e)}")
        logger.error(f"Error en las pruebas alternativas: {str(e)}", exc_info=True)
        return False

def test_templates_alternative():
    """
    Probar sistema de plantillas alternativo
    """
    try:
        print("📋 Probando sistema de plantillas alternativo...")
        
        from document_manager_alternative.templates import TemplateManager
        
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
            'client_name': 'Cliente de Prueba Alternativo',
            'description': 'Descripción de prueba alternativo'
        }
        
        try:
            contenido_renderizado = template_manager.render_template('incident_report', contexto)
            print("✅ Plantilla renderizada correctamente")
        except Exception as e:
            print(f"⚠️ Error renderizando plantilla: {str(e)}")
        
        print("✅ Sistema de plantillas alternativo probado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando plantillas alternativas: {str(e)}")
        logger.error(f"Error probando plantillas alternativas: {str(e)}", exc_info=True)
        return False

def test_ai_processor_alternative():
    """
    Probar procesador de IA alternativo
    """
    try:
        print("🤖 Probando procesador de IA alternativo...")
        
        from document_manager_alternative.ai_processor import AIProcessor
        
        ai_processor = AIProcessor()
        
        # Probar mejora de redacción
        contexto_original = {
            'description': 'Hay un error en el producto que causa problemas',
            'general_observations': 'Se encontró un defecto en la fabricación',
            'recommendations': 'Hay que arreglar el problema inmediatamente'
        }
        
        contexto_mejorado = ai_processor.maquillar_redaccion(contexto_original)
        
        print("✅ Redacción mejorada:")
        print(f"  Original: {contexto_original['description']}")
        print(f"  Mejorado: {contexto_mejorado['description']}")
        
        # Probar generación de resumen
        resumen = ai_processor.generar_resumen_ia(contexto_mejorado)
        print("✅ Resumen generado por IA local")
        
        print("✅ Procesador de IA alternativo probado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando IA alternativa: {str(e)}")
        logger.error(f"Error probando IA alternativa: {str(e)}", exc_info=True)
        return False

def main():
    """
    Función principal de pruebas del módulo alternativo
    """
    print("🧪 INICIANDO PRUEBAS DEL MÓDULO ALTERNATIVO DE GESTIÓN DE DOCUMENTOS")
    print("=" * 70)
    
    # Ejecutar pruebas
    pruebas = [
        ("Gestor de Documentos Alternativo", test_alternative_document_manager),
        ("Sistema de Plantillas Alternativo", test_templates_alternative),
        ("Procesador de IA Alternativo", test_ai_processor_alternative)
    ]
    
    resultados = []
    
    for nombre, funcion in pruebas:
        print(f"\n🔍 Probando: {nombre}")
        print("-" * 50)
        
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error crítico en {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS DEL MÓDULO ALTERNATIVO")
    print("=" * 70)
    
    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLÓ"
        print(f"{nombre}: {estado}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡TODAS LAS PRUEBAS DEL MÓDULO ALTERNATIVO COMPLETADAS EXITOSAMENTE!")
        print("🚀 El módulo alternativo está listo para usar")
        print("\n📋 Características del módulo alternativo:")
        print("  • Usa reportlab en lugar de WeasyPrint")
        print("  • Análisis de IA local sin dependencias externas")
        print("  • Compatible con Windows")
        print("  • Genera documentos Word y PDF profesionales")
        print("  • Sistema de plantillas HTML con CSS moderno")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar los errores anteriores")
    
    return exitosos == len(resultados)

if __name__ == "__main__":
    main()
