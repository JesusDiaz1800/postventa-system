#!/usr/bin/env python
"""
Script para configurar la estructura de carpetas de documentos
"""
import os
import sys
from pathlib import Path

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / 'documents'

print(f"BASE_DIR: {BASE_DIR}")
print(f"DOCUMENTS_DIR: {DOCUMENTS_DIR}")
print(f"Documents dir exists: {DOCUMENTS_DIR.exists()}")

# Crear estructura de carpetas si no existe
if not DOCUMENTS_DIR.exists():
    print("Creando directorio de documentos...")
    DOCUMENTS_DIR.mkdir(exist_ok=True)

# Crear subdirectorios
subdirs = [
    'visit_reports',
    'lab_reports', 
    'supplier_reports',
    'quality_reports',
    'incident_attachments',
    'shared'
]

for subdir in subdirs:
    subdir_path = DOCUMENTS_DIR / subdir
    if not subdir_path.exists():
        print(f"Creando subdirectorio: {subdir}")
        subdir_path.mkdir(exist_ok=True)
    
    # Crear subdirectorios para incidencias específicas
    if subdir == 'visit_reports':
        incident_dir = subdir_path / 'incident_88'
        if not incident_dir.exists():
            print(f"Creando directorio de incidencia: {incident_dir}")
            incident_dir.mkdir(exist_ok=True)

print("Estructura de carpetas creada exitosamente!")
print(f"Contenido de {DOCUMENTS_DIR}:")
for item in DOCUMENTS_DIR.iterdir():
    print(f"  - {item.name}")

# Verificar configuración de Django
try:
    import django
    from django.conf import settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    django.setup()
    
    shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
    print(f"\nSHARED_DOCUMENTS_PATH configurado: {shared_path}")
    print(f"SHARED_DOCUMENTS_PATH existe: {os.path.exists(shared_path) if shared_path else False}")
    
except Exception as e:
    print(f"Error al verificar configuración de Django: {e}")
