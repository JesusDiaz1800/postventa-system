#!/usr/bin/env python
"""
Script para corregir la tabla incidents agregando la columna responsable
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from django.db import connection

def fix_incidents_table_final():
    """Corregir la tabla incidents agregando la columna responsable"""
    try:
        print("Corrigiendo tabla incidents...")
        
        with connection.cursor() as cursor:
            # Verificar si la columna responsable existe
            cursor.execute("PRAGMA table_info(incidents)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"Columnas existentes: {len(column_names)}")
            
            # Verificar si falta la columna responsable
            if 'responsable' not in column_names:
                print("Agregando columna responsable...")
                cursor.execute("ALTER TABLE incidents ADD COLUMN responsable VARCHAR(200)")
                print("[OK] Columna responsable agregada")
            else:
                print("[OK] Columna responsable ya existe")
            
            # Verificar otras columnas que podrían faltar
            required_columns = ['assigned_to_id', 'closed_by_id', 'created_by_id']
            for col in required_columns:
                if col not in column_names:
                    print(f"Agregando columna {col}...")
                    if col.endswith('_id'):
                        cursor.execute(f"ALTER TABLE incidents ADD COLUMN {col} INTEGER")
                    else:
                        cursor.execute(f"ALTER TABLE incidents ADD COLUMN {col} VARCHAR(200)")
                    print(f"[OK] Columna {col} agregada")
                else:
                    print(f"[OK] Columna {col} ya existe")
            
            # Verificar la estructura final
            cursor.execute("PRAGMA table_info(incidents)")
            final_columns = cursor.fetchall()
            print(f"\nEstructura final de la tabla incidents:")
            for col in final_columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Verificar datos existentes
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"\n[OK] Total de incidencias: {count}")
            
            if count > 0:
                # Mostrar una incidencia de ejemplo
                cursor.execute("SELECT code, cliente, estado FROM incidents LIMIT 1")
                incident = cursor.fetchone()
                if incident:
                    print(f"[OK] Incidencia de ejemplo: {incident[0]} - {incident[1]} - {incident[2]}")
            
        print("\n[OK] Tabla incidents corregida exitosamente")
        
    except Exception as e:
        print(f"[ERROR] Error corrigiendo tabla: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_incidents_table_final()
