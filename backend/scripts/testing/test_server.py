#!/usr/bin/env python3
"""
Script para probar el servidor Django
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

try:
    from apps.documents.document_generator import document_generator
    print("✅ DocumentGenerator importado correctamente")
except Exception as e:
    print(f"❌ Error importando DocumentGenerator: {e}")

try:
    from apps.documents.views import generate_polifusion_lab_report
    print("✅ Vistas de documentos importadas correctamente")
except Exception as e:
    print(f"❌ Error importando vistas: {e}")

try:
    from apps.documents.download_views import download_document
    print("✅ Vistas de descarga importadas correctamente")
except Exception as e:
    print(f"❌ Error importando vistas de descarga: {e}")

print("\n🎉 ¡Todas las importaciones funcionan correctamente!")
print("📋 El servidor debería iniciar sin problemas.")
print("🚀 Ejecuta: python manage.py runserver 0.0.0.0:8000")
