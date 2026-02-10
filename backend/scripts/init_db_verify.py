
import pyodbc

server = '192.168.1.145'
database = 'master' # Connect to master first

# Common drivers to try in order of preference
drivers = [
    '{ODBC Driver 18 for SQL Server}',
    '{ODBC Driver 17 for SQL Server}',
    '{SQL Server Native Client 11.0}',
    '{SQL Server}'
]

print("Available ODBC Drivers:")
for d in pyodbc.drivers():
    print(f" - {d}")

conn = None
for driver in drivers:
    try:
        print(f"\nTrying driver: {driver}...")
        # Adjust params based on driver
        # Now using SQL Auth (sa/Sistemas2025)
        params = 'UID=sa;PWD=Sistemas2025;Encrypt=no;TrustServerCertificate=yes'
            
        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};{params}'
        conn = pyodbc.connect(conn_str, autocommit=True)
        print(f"SUCCESS! Connected using {driver}")
        break
    except Exception as e:
        print(f"Failed with {driver}: {e}")

if conn:
    try:
        cursor = conn.cursor()
        print("Checking if database 'postventa_system' exists...")
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'postventa_system'")
        if not cursor.fetchone():
            print("Creating database 'postventa_system'...")
            cursor.execute("CREATE DATABASE postventa_system")
            print("Database created successfully!")
        else:
            print("Database 'postventa_system' already exists.")
        conn.close()
    except Exception as e:
        print(f"Error during DB operations: {e}")
else:
    print("\nCOULD NOT CONNECT with any known driver. Please install ODBC Driver 17 or 18.")
