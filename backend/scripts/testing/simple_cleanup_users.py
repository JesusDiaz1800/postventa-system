#!/usr/bin/env python
"""
Script simple para limpiar usuarios y configurar usuario real
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def simple_cleanup_users():
    """Limpiar usuarios de manera simple"""
    try:
        print("Limpiando usuarios de prueba...")
        
        # Eliminar usuarios usando SQL directo
        with connection.cursor() as cursor:
            # Eliminar usuarios de prueba
            test_users = ['admin', 'testuser', 'simpleuser', 'customuser', 'djangouser', 'debuguser']
            
            for username in test_users:
                cursor.execute("DELETE FROM users_user WHERE username = %s", [username])
                print(f"  - Usuario '{username}' eliminado")
        
        print("\nConfigurando usuario administrador real...")
        
        # Crear usuario administrador real
        with connection.cursor() as cursor:
            # Verificar si existe
            cursor.execute("SELECT id FROM users_user WHERE username = %s", ['jdiaz@polifusion.cl'])
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar contraseña
                from django.contrib.auth.hashers import make_password
                hashed_password = make_password('adminJDR')
                cursor.execute("""
                    UPDATE users_user 
                    SET password = %s, 
                        email = %s,
                        first_name = %s,
                        last_name = %s,
                        is_staff = 1,
                        is_superuser = 1,
                        is_active = 1,
                        role = %s
                    WHERE username = %s
                """, [hashed_password, 'jdiaz@polifusion.cl', 'Jesus', 'Diaz', 'admin', 'jdiaz@polifusion.cl'])
                print("  - Usuario administrador 'jdiaz@polifusion.cl' actualizado")
            else:
                # Crear nuevo usuario
                from django.contrib.auth.hashers import make_password
                hashed_password = make_password('adminJDR')
                cursor.execute("""
                    INSERT INTO users_user (
                        username, email, password, first_name, last_name,
                        is_staff, is_superuser, is_active, role, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, 1, 1, 1, %s, datetime('now'), datetime('now')
                    )
                """, ['jdiaz@polifusion.cl', 'jdiaz@polifusion.cl', hashed_password, 'Jesus', 'Diaz', 'admin'])
                print("  - Usuario administrador 'jdiaz@polifusion.cl' creado")
        
        # Verificar usuarios restantes
        print(f"\nUsuarios en el sistema:")
        with connection.cursor() as cursor:
            cursor.execute("SELECT username, email, role FROM users_user")
            users = cursor.fetchall()
            for user in users:
                print(f"  - {user[0]} ({user[1]}) - {user[2]}")
        
        print(f"\nTotal de usuarios: {len(users)}")
        
        # Probar autenticación
        print("\nProbando autenticación...")
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='jdiaz@polifusion.cl', password='adminJDR')
        if auth_user:
            print("[OK] Autenticación del administrador exitosa!")
        else:
            print("[ERROR] Autenticación del administrador falló")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_cleanup_users()
