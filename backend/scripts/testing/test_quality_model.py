#!/usr/bin/env python
"""
Script de prueba para verificar el modelo QualityReport
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

try:
    from apps.documents.models import QualityReport
    print("✓ Modelo QualityReport importado correctamente")
    
    # Verificar campos del modelo
    fields = QualityReport._meta.get_fields()
    print(f"✓ Modelo tiene {len(fields)} campos")
    
    # Verificar choices
    report_type_choices = QualityReport._meta.get_field('report_type').choices
    print(f"✓ Choices de report_type: {report_type_choices}")
    
    print("✓ Modelo QualityReport está funcionando correctamente")
    
except Exception as e:
    print(f"✗ Error con el modelo QualityReport: {e}")
    import traceback
    traceback.print_exc()
