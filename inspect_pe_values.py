import os
import django
import sys
from django.db import connections

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def inspect_pe_values():
    db_alias = 'sap_db_pe'
    print(f"Inspecting values for last 3 Service Calls in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Query the last 3 Service Calls with interesting columns
            query = """
                SELECT TOP 3 callID, DocNum, technician, U_NX_VENDEDOR, U_NX_NOM_PRO, subject
                FROM OSCL
                ORDER BY callID DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                print(f"Call {row[0]} (Doc {row[1]}):")
                print(f" - Subject: {row[5]}")
                print(f" - technician: {row[2]}")
                print(f" - U_NX_VENDEDOR: {row[3]}")
                print(f" - U_NX_NOM_PRO: {row[4]}")
                print("-" * 20)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_pe_values()
