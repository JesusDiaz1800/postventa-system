#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.users.models import User
from apps.incidents.models import Category, Responsible

# Crear usuario admin
if not User.objects.filter(email="jdiaz@polifusion.cl").exists():
    User.objects.create_superuser(
        email="jdiaz@polifusion.cl",
        username="jdiaz", 
        password="adminJDR",
        first_name="Jose",
        last_name="Diaz Rodriguez",
        role="admin"
    )
    print("Usuario admin creado")

# Crear categorías
categories = ['Defecto de fabricación', 'Instalación incorrecta', 'Daño en transporte', 'Problema de diseño', 'Otro']
for cat_name in categories:
    Category.objects.get_or_create(name=cat_name)
print(f"Categorías creadas: {len(categories)}")

# Crear responsables  
responsables = ['Calidad', 'Producción', 'Logística', 'Servicio Técnico', 'Gerencia']
for resp_name in responsables:
    Responsible.objects.get_or_create(name=resp_name)
print(f"Responsables creados: {len(responsables)}")

print("Inicialización completada exitosamente")
