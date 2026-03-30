import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def debug_ohem():
    db_alias = 'sap_db_co'
    print(f"Inspecting OHEM table in {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # 1. Get column names
            cursor.execute("SELECT TOP 1 * FROM OHEM")
            columns = [column[0] for column in cursor.description]
            print("\nColumns found in OHEM:")
            print(", ".join(columns))
            
            # 2. Check Active values if column exists
            active_col = None
            for c in columns:
                if c.lower() == 'active':
                    active_col = c
                    break
            
            if active_col:
                cursor.execute(f"SELECT DISTINCT {active_col} FROM OHEM")
                values = [str(r[0]) for r in cursor.fetchall()]
                print(f"\nDistinct values for {active_col}: {values}")
            else:
                print("\nWARNING: 'Active' column not found!")

            # 3. Look for technician-related columns
            tech_cols = [c for c in columns if 'tech' in c.lower() or 'role' in c.lower() or 'pos' in c.lower()]
            print(f"\nPotential technician/role columns: {tech_cols}")
            
            # 4. Show a few rows
            print("\nSample rows (empID, firstName, lastName, role, position, any potential tech col):")
            cols_to_show = ['empID', 'firstName', 'lastName']
            if 'role' in columns: cols_to_show.append('role')
            if 'position' in columns: cols_to_show.append('position')
            for tc in tech_cols:
                if tc not in cols_to_show: cols_to_show.append(tc)
                
            query = f"SELECT TOP 5 {', '.join(cols_to_show)} FROM OHEM"
            cursor.execute(query)
            for row in cursor.fetchall():
                print(row)

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_ohem()
