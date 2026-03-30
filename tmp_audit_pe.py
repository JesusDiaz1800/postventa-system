import pyodbc
import os
import json

# Database configuration for TSTPOLPERU from .env
server = '192.168.1.232,1433'
database = 'TSTPOLPERU'
username = 'ccalidad'
password = 'Plf2025**'
driver = '{ODBC Driver 13 for SQL Server}'

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=no;TrustServerCertificate=yes;'

def run_query(query):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        try:
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            conn.close()
            return results
        except:
            conn.close()
            return "No results"
    except Exception as e:
        return str(e)

print("--- AUDIT EMPLOYEES FLAGS (OHEM) ---")
# technician is a 'tYES'/'tNO' field in many SAP B1 versions
print(json.dumps(run_query("SELECT empID, firstName, lastName, technician, salesPrson FROM OHEM WHERE empID IN (13, 31)"), indent=2))

print("\n--- OSCL COLUMNS ---")
# List columns of OSCL
print(json.dumps(run_query("SELECT TOP 0 * FROM OSCL"), indent=2))
