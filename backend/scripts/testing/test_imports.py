#!/usr/bin/env python3
"""
Script para probar las importaciones necesarias
"""

import sys
import os

print("🔍 PROBANDO IMPORTACIONES")
print("=" * 40)

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("1. Probando importación de docx...")
    from docx import Document
    print("   ✅ docx importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando docx: {e}")

try:
    print("2. Probando importación de docxtpl...")
    from docxtpl import DocxTemplate
    print("   ✅ docxtpl importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando docxtpl: {e}")

try:
    print("3. Probando importación de docxcompose...")
    import docxcompose
    print("   ✅ docxcompose importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando docxcompose: {e}")

try:
    print("4. Probando importación de Django...")
    import django
    print("   ✅ Django importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando Django: {e}")

print("\n🎯 VERIFICANDO VERSIÓN DE PYTHON:")
print(f"   Python: {sys.version}")
print(f"   Path: {sys.executable}")

print("\n📦 VERIFICANDO PAQUETES INSTALADOS:")
try:
    import pkg_resources
    
    packages = ['python-docx', 'docxtpl', 'docxcompose', 'Django']
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"   ✅ {package}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"   ❌ {package}: No encontrado")
except ImportError:
    print("   ❌ pkg_resources no disponible")
