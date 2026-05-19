import os
import sys

# Get absolute path of backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def main():
    for db in ['sap_db', 'sap_db_pe', 'sap_db_co']:
        try:
            with connections[db].cursor() as cursor:
                cursor.execute("SELECT DISTINCT T0.empID, (T0.firstName + ' ' + T0.lastName) as Name FROM OHEM T0 INNER JOIN HEM6 T1 ON T0.empID = T1.empID WHERE T0.Active = 'Y' AND T1.roleID = 2")
                print(f"{db} TECHS with roleID=2:", cursor.fetchall())
                
                cursor.execute("SELECT DISTINCT T1.roleID FROM OHEM T0 INNER JOIN HEM6 T1 ON T0.empID = T1.empID WHERE T0.Active = 'Y'")
                print(f"{db} ROLES:", cursor.fetchall())
        except Exception as e:
            print(f"Error on {db}:", e)

if __name__ == "__main__":
    main()
