#!/usr/bin/env python3
"""
Script para probar sin autenticación
"""

import os
import sys
import django
import json
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.test import RequestFactory
from apps.users.models import User
from apps.documents.document_generator import document_generator
import traceback

def test_without_auth():
    """Probar sin autenticación"""
    
    print("🧪 PROBANDO SIN AUTENTICACIÓN")
    print("=" * 60)
    
    try:
        # Datos de prueba
        test_data = {
            'solicitante': 'POLIFUSIÓN',
            'fecha_solicitud': '2024-01-15',
            'cliente': 'POLIFUSIÓN',
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
        
        print("📋 Datos de prueba:")
        for key, value in test_data.items():
            print(f"   {key}: {value}")
        
        print("\n🔄 Probando generación directa del documento...")
        
        # Probar generación directa del documento
        result = document_generator.generate_polifusion_lab_report(test_data)
        
        if result['success']:
            print(f"✅ Documento generado exitosamente")
            print(f"📄 Archivo DOCX: {result['docx_path']}")
            print(f"📝 Plantilla usada: {result['template_used']}")
            
            # Verificar archivo
            if os.path.exists(result['docx_path']):
                docx_size = os.path.getsize(result['docx_path'])
                print(f"✅ DOCX existe ({docx_size:,} bytes)")
            else:
                print(f"❌ DOCX no encontrado")
        else:
            print(f"❌ Error generando documento: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        print("📋 Traceback completo:")
        traceback.print_exc()
    
    print("\n🎉 ¡PRUEBA COMPLETADA!")

if __name__ == "__main__":
    try:
        test_without_auth()
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        traceback.print_exc()
        sys.exit(1)
