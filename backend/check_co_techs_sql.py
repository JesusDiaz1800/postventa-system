import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def check_technicians():
    db_alias = 'sap_db_co'
    print(f"Checking OHEM table in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # 1. Total active employees
            cursor.execute("SELECT COUNT(*) FROM OHEM WHERE Active = 'Y'")
            active_count = cursor.fetchone()[0]
            print(f"Active employees (Active='Y'): {active_count}")
            
            # 2. Total technicians
            cursor.execute("SELECT COUNT(*) FROM OHEM WHERE technician = 'Y'")
            tech_count = cursor.fetchone()[0]
            print(f"Technicians (technician='Y'): {tech_count}")
            
            # 3. List some technicians if any
            if tech_count > 0:
                print("\nValid Technicians:")
                cursor.execute("SELECT empID, firstName, lastName FROM OHEM WHERE technician = 'Y' AND Active = 'Y'")
                for row in cursor.fetchall():
                    print(f" - ID: {row[0]}, Name: {row[1]} {row[2]}")
            
            # 4. Check specific names the user mentioned
            print("\nChecking specific employees mentioned by user:")
            names = ['CRISTIAN', 'JESUS', 'DAVID']
            for name in names:
                cursor.execute(f"SELECT empID, firstName, lastName, Active, technician FROM OHEM WHERE firstName LIKE '%{name}%'")
                row = cursor.fetchone()
                if row:
                    print(f"Found: ID={row[0]}, Name={row[1]} {row[2]}, Active={row[3]}, Technician={row[4]}")
                else:
                    print(f"Not found: {name}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_technicians()
