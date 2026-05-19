#!/usr/bin/env python
import os
import sys

print("=== PRUEBA SIMPLE ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    import django
    print(f"Django version: {django.get_version()}")
except ImportError as e:
    print(f"Error importing Django: {e}")

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    django.setup()
    print("Django setup successful")
except Exception as e:
    print(f"Error setting up Django: {e}")
    import traceback
    traceback.print_exc()