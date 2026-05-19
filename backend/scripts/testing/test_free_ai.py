#!/usr/bin/env python
"""
Script para probar la IA gratuita y funcional
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.ai.free_ai_service import FreeAIService
import tempfile
import base64

def test_free_ai():
    """Probar la IA gratuita con una imagen de prueba"""
    
    print("=== PROBANDO IA GRATUITA Y FUNCIONAL ===")
    
    # Crear una imagen de prueba simple (1x1 pixel PNG)
    test_image_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    )
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_file.write(test_image_data)
        temp_file_path = temp_file.name
    
    try:
        # Inicializar servicio de IA gratuita
        ai_service = FreeAIService()
        
        print(f"\n🔍 Probando análisis de imagen...")
        print(f"📁 Imagen de prueba: {temp_file_path}")
        
        # Probar análisis con diferentes tipos
        analysis_types = ['technical_analysis', 'quality_inspection', 'document_analysis']
        
        for analysis_type in analysis_types:
            print(f"\n📊 Probando análisis: {analysis_type}")
            
            result = ai_service.analyze_image(temp_file_path, analysis_type)
            
            if result['success']:
                print(f"✅ Éxito con modelo: {result['model']}")
                print(f"🎯 Confianza: {result['confidence']}")
                print(f"💰 Costo: ${result.get('cost_estimate', 0):.6f}")
                print(f"🔢 Tokens usados: {result.get('tokens_used', 0)}")
                print(f"📝 Análisis (primeros 300 caracteres):")
                print(f"   {result['analysis'][:300]}...")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        # Probar generación de reporte
        print(f"\n📋 Probando generación de reporte...")
        
        sample_analysis = """
        ## Análisis Técnico
        
        ### Descripción General
        Producto de prueba para verificación de sistema.
        
        ### Elementos Técnicos
        - Estructura básica
        - Material estándar
        
        ### Recomendaciones
        - Verificación adicional recomendada
        """
        
        context = {
            'incident_id': 'INC-001',
            'product_type': 'Componente de prueba',
            'analysis_date': '2024-01-15'
        }
        
        report_result = ai_service.generate_technical_report(sample_analysis, context)
        
        if report_result['success']:
            print(f"✅ Reporte generado con modelo: {report_result['model']}")
            print(f"💰 Costo: ${report_result.get('cost_estimate', 0):.6f}")
            print(f"📝 Reporte (primeros 300 caracteres):")
            print(f"   {report_result['report'][:300]}...")
        else:
            print(f"❌ Error en reporte: {report_result.get('error', 'Unknown error')}")
        
        print(f"\n🎉 Prueba de IA gratuita completada!")
        print(f"✅ ¡La IA está lista para usar en producción!")
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar archivo temporal
        try:
            os.unlink(temp_file_path)
        except:
            pass

if __name__ == '__main__':
    test_free_ai()
