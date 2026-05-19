#!/usr/bin/env python3
"""
Script para verificar el estado del servidor
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line

def check_server_status():
    """Verificar el estado del servidor"""
    
    print("🔍 VERIFICANDO ESTADO DEL SERVIDOR")
    print("=" * 60)
    
    try:
        # 1. Verificar configuración de Django
        print("1️⃣ CONFIGURACIÓN DE DJANGO:")
        print(f"   📁 DEBUG: {settings.DEBUG}")
        print(f"   📁 ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   📁 DATABASE: {settings.DATABASES['default']['NAME']}")
        
        # 2. Verificar aplicaciones instaladas
        print("\n2️⃣ APLICACIONES INSTALADAS:")
        for app in settings.INSTALLED_APPS:
            if app.startswith('apps.'):
                print(f"   ✅ {app}")
        
        # 3. Verificar URLs
        print("\n3️⃣ VERIFICANDO URLs:")
        try:
            from django.urls import reverse
            from django.test import Client
            
            client = Client()
            
            # Probar URL de login
            try:
                response = client.get('/api/auth/login/')
                print(f"   ✅ /api/auth/login/ - Status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ /api/auth/login/ - Error: {e}")
            
            # Probar URL de documentos
            try:
                response = client.get('/api/documents/')
                print(f"   ✅ /api/documents/ - Status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ /api/documents/ - Error: {e}")
                
        except Exception as e:
            print(f"   ❌ Error verificando URLs: {e}")
        
        # 4. Verificar base de datos
        print("\n4️⃣ VERIFICANDO BASE DE DATOS:")
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    print("   ✅ Conexión a base de datos OK")
                else:
                    print("   ❌ Error en consulta de base de datos")
        except Exception as e:
            print(f"   ❌ Error de base de datos: {e}")
        
        # 5. Verificar modelos
        print("\n5️⃣ VERIFICANDO MODELOS:")
        try:
            from apps.documents.models import Document
            from apps.users.models import User
            
            doc_count = Document.objects.count()
            user_count = User.objects.count()
            
            print(f"   ✅ Documentos en BD: {doc_count}")
            print(f"   ✅ Usuarios en BD: {user_count}")
            
        except Exception as e:
            print(f"   ❌ Error verificando modelos: {e}")
        
        print("\n🎉 ¡VERIFICACIÓN COMPLETADA!")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        check_server_status()
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
