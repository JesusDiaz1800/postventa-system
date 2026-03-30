import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections
from apps.core.thread_local import set_current_country

def check_roles():
    set_current_country('PE')
    print("Verificando flags de rol en OHEM (PE)...")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            # En B1, el rol de técnico suele ser un checkbox. 
            # Vamos a listar todas las columnas que empiecen con 'U_' o nombres comunes.
            cursor.execute("SELECT TOP 5 empID, firstName, lastName, Active FROM OHEM")
            columns = [col[0] for col in cursor.description]
            print(f"Columns: {columns}")
            
            # Buscamos columnas de roles
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'OHEM' AND (COLUMN_NAME LIKE '%Role%' OR COLUMN_NAME LIKE '%Tech%' OR COLUMN_NAME LIKE '%Sales%')")
            role_cols = [row[0] for row in cursor.fetchall()]
            print(f"Role/Tech Columns found: {role_cols}")
            
            if role_cols:
                query = f"SELECT empID, firstName, {', '.join(role_cols)} FROM OHEM WHERE empID IN (1, 13)"
                cursor.execute(query)
                for row in cursor.fetchall():
                    print(row)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_roles()
