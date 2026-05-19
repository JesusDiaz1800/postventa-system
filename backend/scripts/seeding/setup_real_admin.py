#!/usr/bin/env python
"""
Script para configurar el usuario administrador real
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def setup_real_admin():
    """Configurar el usuario administrador real"""
    try:
        print("Configurando usuario administrador real...")
        
        with connection.cursor() as cursor:
            # Crear usuario en tabla users (modelo personalizado)
            from django.contrib.auth.hashers import make_password
            hashed_password = make_password('adminJDR')
            
            # Verificar si existe
            cursor.execute("SELECT id FROM users WHERE username = %s", ['jdiaz@polifusion.cl'])
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar
                cursor.execute("""
                    UPDATE users 
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
                print("  - Usuario administrador 'jdiaz@polifusion.cl' actualizado en tabla users")
            else:
                # Crear nuevo
                cursor.execute("""
                    INSERT INTO users (
                        username, email, password, first_name, last_name,
                        is_staff, is_superuser, is_active, role, created_at, updated_at, date_joined
                    ) VALUES (
                        %s, %s, %s, %s, %s, 1, 1, 1, %s, datetime('now'), datetime('now'), datetime('now')
                    )
                """, ['jdiaz@polifusion.cl', 'jdiaz@polifusion.cl', hashed_password, 'Jesus', 'Diaz', 'admin'])
                print("  - Usuario administrador 'jdiaz@polifusion.cl' creado en tabla users")
            
            # También crear en auth_user para compatibilidad
            cursor.execute("SELECT id FROM auth_user WHERE username = %s", ['jdiaz@polifusion.cl'])
            existing_auth = cursor.fetchone()
            
            if existing_auth:
                # Actualizar
                cursor.execute("""
                    UPDATE auth_user 
                    SET password = %s, 
                        email = %s,
                        first_name = %s,
                        last_name = %s,
                        is_staff = 1,
                        is_superuser = 1,
                        is_active = 1
                    WHERE username = %s
                """, [hashed_password, 'jdiaz@polifusion.cl', 'Jesus', 'Diaz', 'jdiaz@polifusion.cl'])
                print("  - Usuario administrador 'jdiaz@polifusion.cl' actualizado en tabla auth_user")
            else:
                # Crear nuevo
                cursor.execute("""
                    INSERT INTO auth_user (
                        username, email, password, first_name, last_name,
                        is_staff, is_superuser, is_active, date_joined, last_login
                    ) VALUES (
                        %s, %s, %s, %s, %s, 1, 1, 1, datetime('now'), NULL
                    )
                """, ['jdiaz@polifusion.cl', 'jdiaz@polifusion.cl', hashed_password, 'Jesus', 'Diaz'])
                print("  - Usuario administrador 'jdiaz@polifusion.cl' creado en tabla auth_user")
        
        # Verificar usuarios restantes
        print(f"\nUsuarios en el sistema:")
        with connection.cursor() as cursor:
            # Verificar tabla users
            cursor.execute("SELECT username, email, role FROM users")
            users_custom = cursor.fetchall()
            print("Tabla users:")
            for user in users_custom:
                print(f"  - {user[0]} ({user[1]}) - {user[2]}")
            
            # Verificar tabla auth_user
            cursor.execute("SELECT username, email FROM auth_user")
            users_auth = cursor.fetchall()
            print("\nTabla auth_user:")
            for user in users_auth:
                print(f"  - {user[0]} ({user[1]})")
        
        print(f"\nTotal de usuarios en users: {len(users_custom)}")
        print(f"Total de usuarios en auth_user: {len(users_auth)}")
        
        # Probar autenticación
        print("\nProbando autenticación...")
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='jdiaz@polifusion.cl', password='adminJDR')
        if auth_user:
            print("[OK] Autenticación del administrador exitosa!")
            print(f"Usuario autenticado: {auth_user.username}")
            print(f"Email: {auth_user.email}")
            print(f"Role: {getattr(auth_user, 'role', 'N/A')}")
        else:
            print("[ERROR] Autenticación del administrador falló")
        
        print(f"\n✅ CONFIGURACIÓN COMPLETADA")
        print(f"📧 Usuario: jdiaz@polifusion.cl")
        print(f"🔑 Contraseña: adminJDR")
        print(f"👤 Nombre: Jesus Diaz")
        print(f"🔧 Rol: Administrador")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_real_admin()
