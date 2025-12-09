#!/usr/bin/env python
"""
Script para inicializar datos de producción
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
from django.db import transaction

def init_data():
    """Inicializa datos básicos para producción"""
    print("=" * 60)
    print("INICIALIZANDO DATOS DE PRODUCCION")
    print("=" * 60)
    
    with transaction.atomic():
        # 1. Crear usuario administrador si no existe
        print("\n1. Verificando usuario administrador...")
        admin_email = "jdiaz@polifusion.cl"
        if not User.objects.filter(email=admin_email).exists():
            admin = User.objects.create_superuser(
                email=admin_email,
                username="jdiaz",
                password="adminJDR",
                full_name="Jose Diaz Rodriguez",
                role="admin"
            )
            print(f"✓ Usuario administrador creado: {admin_email}")
        else:
            print(f"✓ Usuario administrador ya existe: {admin_email}")
        
        # 2. Crear categorías básicas si no existen
        print("\n2. Verificando categorías...")
        categories = [
            'Defecto de fabricación',
            'Instalación incorrecta',
            'Daño en transporte',
            'Problema de diseño',
            'Otro'
        ]
        
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(nombre=cat_name)
            if created:
                print(f"  ✓ Categoría creada: {cat_name}")
        
        print(f"✓ Total de categorías: {Category.objects.count()}")
        
        # 3. Crear responsables básicos si no existen
        print("\n3. Verificando responsables...")
        responsables = [
            'Calidad',
            'Producción',
            'Logística',
            'Servicio Técnico',
            'Gerencia'
        ]
        
        for resp_name in responsables:
            resp, created = Responsible.objects.get_or_create(nombre=resp_name)
            if created:
                print(f"  ✓ Responsable creado: {resp_name}")
        
        print(f"✓ Total de responsables: {Responsible.objects.count()}")
        
    print("\n" + "=" * 60)
    print("INICIALIZACION COMPLETADA")
    print("=" * 60)
    print("\nDatos básicos listos para producción:")
    print(f"  - Usuarios: {User.objects.count()}")
    print(f"  - Categorías: {Category.objects.count()}")
    print(f"  - Responsables: {Responsible.objects.count()}")
    print("\nCredenciales:")
    print(f"  Email: {admin_email}")
    print(f"  Contraseña: adminJDR")
    print("\n✓ Sistema listo para usar")

if __name__ == '__main__':
    try:
        init_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

