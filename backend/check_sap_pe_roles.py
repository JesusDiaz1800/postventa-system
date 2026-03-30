import os
import django
from django.db import connections

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_sap_roles():
    print("--- Roles definidos en SAP (OROL) ---")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT RoleID, Name, Descr from OROL")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Name: {row[1]}, Descr: {row[2]}")
            
            print("\n--- Roles asignados en HEM6 ---")
            cursor.execute("""
                SELECT T0.empID, T0.firstName, T0.lastName, T1.roleID 
                FROM OHEM T0 
                INNER JOIN HEM6 T1 ON T0.empID = T1.empID 
                WHERE T0.Active = 'Y'
            """)
            for row in cursor.fetchall()[:20]:
                print(f"Emp: {row[1]} {row[2]} (ID: {row[0]}), RoleID: {row[3]}")
    except Exception as e:
        print(f"Error consultando roles SAP PE: {e}")

if __name__ == "__main__":
    check_sap_roles()
