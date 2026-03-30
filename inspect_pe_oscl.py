import os
import django
import sys
from django.db import connections

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def inspect_pe_service_call():
    db_alias = 'sap_db_pe'
    print(f"Inspecting a real Service Call in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Query the last Service Call
            query = """
                SELECT TOP 1 callID, DocNum, technician, HandledBy, U_nx_tecnico
                FROM OSCL
                ORDER BY callID DESC
            """
            # Probar si U_nx_tecnico existe, si falla quitarlo
            try:
                cursor.execute(query)
            except:
                cursor.execute("SELECT TOP 1 callID, DocNum, technician, HandledBy FROM OSCL ORDER BY callID DESC")
                
            row = cursor.fetchone()
            if row:
                print(f"Sample Service Call found:")
                print(f" - callID: {row[0]}")
                print(f" - DocNum: {row[1]}")
                print(f" - technician (AssigneeCode): {row[2]}")
                print(f" - HandledBy: {row[3]}")
                if len(row) > 4:
                    print(f" - U_nx_tecnico: {row[4]}")
            else:
                print("No Service Calls found in PE.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_pe_service_call()
