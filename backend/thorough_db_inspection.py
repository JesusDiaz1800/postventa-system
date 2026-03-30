import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def thorough_inspection():
    db_alias = 'sap_db_co'
    print(f"Thoroughly inspecting {db_alias}...")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # 1. Get all tables and their row counts
            print("\nTable Row Counts (Top 30):")
            query = """
                SELECT 
                    t.NAME AS TableName,
                    p.rows AS RowCounts
                FROM 
                    sys.tables t
                INNER JOIN      
                    sys.indexes i ON t.OBJECT_ID = i.object_id
                INNER JOIN 
                    sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                WHERE 
                    t.is_ms_shipped = 0
                    AND i.index_id IN (0,1)
                    AND p.rows > 0
                ORDER BY 
                    p.rows DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows[:30]:
                print(f" - {row[0]}: {row[1]}")
            
            # 2. Specifically look for OHEM and OSCL even if 0 rows
            print("\nSpecific Table Check:")
            for tbl in ['OHEM', 'OSCL', 'OCRD', 'OITM', 'OCTG']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
                    count = cursor.fetchone()[0]
                    print(f" - {tbl}: {count} rows")
                except:
                    print(f" - {tbl}: NOT FOUND or Error")

            # 3. Check for any table containing 'Employee' or 'Call' or 'Tech'
            print("\nSearching for related tables by name:")
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE '%Emp%' OR name LIKE '%Call%' OR name LIKE '%Tech%'")
            matches = [r[0] for r in cursor.fetchall()]
            for m in matches:
                cursor.execute(f"SELECT COUNT(*) FROM [{m}]")
                c = cursor.fetchone()[0]
                print(f" - {m}: {c} rows")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    thorough_inspection()
