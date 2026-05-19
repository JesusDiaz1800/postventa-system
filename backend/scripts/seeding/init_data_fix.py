#!/usr/bin/env python
"""
Script para inicializar datos y corregir errores del sistema
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.users.models import User
from apps.incidents.models import Category, Responsible

def init_data():
    """Inicializar datos básicos del sistema"""
    print("🔧 Inicializando datos del sistema...")
    
    # Crear usuario admin si no existe
    if not User.objects.filter(email="jdiaz@polifusion.cl").exists():
        User.objects.create_superuser(
            email="jdiaz@polifusion.cl",
            username="jdiaz",
            password="adminJDR",
            first_name="Jose",
            last_name="Diaz Rodriguez",
            role="admin"
        )
        print("✅ Usuario admin creado")
    else:
        print("✅ Usuario admin ya existe")
    
    # Crear categorías básicas
    categories = ['Defecto de fabricación', 'Instalación incorrecta', 'Daño en transporte', 'Problema de diseño', 'Otro']
    for cat_name in categories:
        Category.objects.get_or_create(name=cat_name)
    print(f"✅ {len(categories)} categorías verificadas")
    
    # Crear responsables básicos
    responsables = ['Calidad', 'Producción', 'Logística', 'Servicio Técnico', 'Gerencia']
    for resp_name in responsables:
        Responsible.objects.get_or_create(name=resp_name)
    print(f"✅ {len(responsables)} responsables verificados")
    
    print("🎉 Datos inicializados correctamente")

if __name__ == '__main__':
    try:
        init_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
