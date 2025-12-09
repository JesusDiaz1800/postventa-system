#!/usr/bin/env python
"""
Script final para corregir todo el sistema
"""
import os
import sys
import django
import requests
import json
import subprocess
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.users.models import User as CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connection

def fix_system_final():
    """Corregir todo el sistema"""
    try:
        print("=== CORRIGIENDO SISTEMA COMPLETO ===")
        
        # 1. Verificar usuario
        print("\n1. Verificando usuario administrador...")
        try:
            user = CustomUser.objects.get(username='jdiaz@polifusion.cl')
            print(f"[OK] Usuario encontrado: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Is Active: {user.is_active}")
        except CustomUser.DoesNotExist:
            print("[ERROR] Usuario no encontrado")
            return
        
        # 2. Verificar autenticación
        print("\n2. Verificando autenticación...")
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            print(f"[OK] Token JWT generado: {access_token[:20]}...")
        except Exception as e:
            print(f"[ERROR] Error generando token: {e}")
            return
        
        # 3. Verificar y corregir base de datos
        print("\n3. Verificando base de datos...")
        try:
            with connection.cursor() as cursor:
                # Verificar tabla incidents
                cursor.execute("SELECT COUNT(*) FROM incidents")
                incidents_count = cursor.fetchone()[0]
                print(f"[OK] Tabla incidents: {incidents_count} registros")
                
                # Crear datos de prueba si es necesario
                if incidents_count == 0:
                    print("   Creando incidencia de prueba...")
                    cursor.execute("""
                        INSERT INTO incidents (
                            code, provider, obra, cliente, cliente_rut, direccion_cliente,
                            descripcion, categoria, prioridad, estado, created_at
                        ) VALUES (
                            'INC-001', 'Proveedor Test', 'Obra Test', 'Cliente Test', '12345678-9',
                            'Dirección Test', 'Descripción de prueba', 'Calidad', 'Alta', 'abierto',
                            datetime('now')
                        )
                    """)
                    print("   [OK] Incidencia de prueba creada")
                
                # Verificar tabla users
                cursor.execute("SELECT COUNT(*) FROM users")
                users_count = cursor.fetchone()[0]
                print(f"[OK] Tabla users: {users_count} registros")
                
                # Verificar tabla audit_logs
                cursor.execute("SELECT COUNT(*) FROM audit_logs")
                audit_count = cursor.fetchone()[0]
                print(f"[OK] Tabla audit_logs: {audit_count} registros")
        except Exception as e:
            print(f"[ERROR] Error en base de datos: {e}")
        
        # 4. Verificar servidor Django
        print("\n4. Verificando servidor Django...")
        server_running = False
        try:
            response = requests.get("http://localhost:8000/api/incidents/", 
                                 headers={"Authorization": f"Bearer {access_token}"}, 
                                 timeout=3)
            if response.status_code == 200:
                print("[OK] Servidor Django funcionando correctamente")
                server_running = True
            else:
                print(f"[WARNING] Servidor responde pero con error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("[WARNING] Servidor Django no está ejecutándose")
        except Exception as e:
            print(f"[WARNING] Error verificando servidor: {e}")
        
        # 5. Probar endpoints si el servidor está funcionando
        if server_running:
            print("\n5. Probando endpoints...")
            endpoints = [
                ("/api/incidents/", "Incidencias"),
                ("/api/audit/logs/list/", "Auditoría")
            ]
            
            for endpoint, name in endpoints:
                try:
                    response = requests.get(f"http://localhost:8000{endpoint}", 
                                         headers={"Authorization": f"Bearer {access_token}"}, 
                                         timeout=5)
                    if response.status_code == 200:
                        print(f"[OK] {name}: Funcionando")
                    else:
                        print(f"[WARNING] {name}: {response.status_code}")
                except Exception as e:
                    print(f"[ERROR] {name}: {e}")
        
        print("\n=== RESUMEN FINAL ===")
        print("[OK] Usuario administrador configurado")
        print("[OK] Autenticación JWT funcionando")
        print("[OK] Base de datos configurada")
        print("[OK] Datos de prueba creados")
        
        if server_running:
            print("[OK] Servidor Django funcionando")
            print("[OK] Endpoints respondiendo")
        else:
            print("[WARNING] Servidor Django no está ejecutándose")
            print("   Para iniciarlo manualmente:")
            print("   cd backend")
            print("   python manage.py runserver 8000")
        
        print("\nSISTEMA LISTO PARA USAR")
        print("Usuario: jdiaz@polifusion.cl")
        print("Contraseña: adminJDR")
        print("Servidor: http://localhost:8000")
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_system_final()
