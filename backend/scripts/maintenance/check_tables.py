#!/usr/bin/env python
"""
Script para verificar las tablas de la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def check_tables():
    """Verificar las tablas de la base de datos"""
    try:
        print("Verificando tablas de la base de datos...")
        
        with connection.cursor() as cursor:
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("Tablas encontradas:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Buscar tabla de usuarios
            user_tables = [t[0] for t in tables if 'user' in t[0].lower()]
            print(f"\nTablas relacionadas con usuarios: {user_tables}")
            
            # Verificar usuarios existentes
            for table in user_tables:
                try:
                    cursor.execute(f"SELECT username, email FROM {table} LIMIT 5")
                    users = cursor.fetchall()
                    print(f"\nUsuarios en {table}:")
                    for user in users:
                        print(f"  - {user[0]} ({user[1]})")
                except Exception as e:
                    print(f"Error consultando {table}: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_tables()