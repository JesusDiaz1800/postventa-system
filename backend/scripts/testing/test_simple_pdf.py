#!/usr/bin/env python
"""
Test simple del generador de PDF ultra profesional
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

try:
    from apps.documents.services.ultra_professional_pdf_generator import UltraProfessionalPDFGenerator
    print("✅ Importación exitosa del generador PDF")
    
    # Datos mínimos de prueba
    test_data = {
        'order_number': 'TEST-001',
        'client_name': 'Cliente Prueba',
        'project_name': 'Proyecto Test',
        'technician': 'Técnico Test'
    }
    
    # Crear generador y probar
    generator = UltraProfessionalPDFGenerator()
    print("✅ Generador creado")
    
    pdf_buffer = generator.generate_visit_report_pdf(test_data)
    print("✅ PDF generado")
    
    # Guardar archivo
    with open('test_pdf_output.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("🎉 ¡PDF ultra profesional generado exitosamente!")
    print(f"📄 Archivo: test_pdf_output.pdf")
    print(f"📏 Tamaño: {len(pdf_buffer.getvalue())} bytes")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
