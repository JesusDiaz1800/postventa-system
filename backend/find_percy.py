import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def find_percy_everywhere():
    cursor = connections['sap_db_pe'].cursor()
    # List of likely databases
    dbs = ['TSTPOLPERU', 'PRDPOLPERU', 'TESTPOLIFUSION', 'VSBDTEST', 'VSBDTEST2', 'TSTPOLFCOLOMBIA', 'TSTPOLCOLOMBIA_2']
    
    for db in dbs:
        try:
            query = f"SELECT empID, firstName, lastName FROM {db}..OHEM WHERE (firstName LIKE '%PERCY%' OR lastName LIKE '%LUEY%') AND Active='Y'"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                print(f"DATABASE {db} FOUND PERCY: {rows}")
            else:
                print(f"DATABASE {db} : No active Percy found.")
        except Exception as e:
            print(f"DATABASE {db} : Error or No access")

if __name__ == "__main__":
    find_percy_everywhere()
