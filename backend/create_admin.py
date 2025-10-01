#!/usr/bin/env python3
"""
Script para crear superusuario admin
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')

# Setup Django
django.setup()

from django.db import connection
from django.contrib.auth.hashers import make_password
from django.utils import timezone

def create_admin():
    """Crear superusuario admin"""
    print("👤 Creando superusuario admin...")
    
    try:
        with connection.cursor() as cursor:
            # Verificar si ya existe
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] > 0:
                print("✅ Superusuario 'admin' ya existe")
                return True
            
            # Crear superusuario
            password = make_password('admin123')
            now = timezone.now()
            
            cursor.execute("""
                INSERT INTO users (username, email, password, first_name, last_name, 
                                 is_staff, is_active, is_superuser, date_joined)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@postventa.local', password, 'Admin', 'Sistema', 
                  1, 1, 1, now))
            
            print("✅ Superusuario 'admin' creado exitosamente")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            return True
            
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False

if __name__ == "__main__":
    create_admin()
