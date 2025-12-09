
import pyodbc

drivers = [d for d in pyodbc.drivers() if 'Driver 17' in d]
if not drivers:
    # Fallback to whatever is there just in case
    drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]

print(f"Using Drivers: {drivers}")

servers = [
    'localhost\\SQLEXPRESS',
    '(localdb)\\mssqllocaldb',
    'localhost',
    '127.0.0.1'
]

for driver in drivers:
    for server in servers:
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
        print(f"Testing: {server} with {driver}...", end='')
        try:
            conn = pyodbc.connect(conn_str, timeout=3)
            print(" SUCCESS!")
            print(f"!!! VALID CONFIG FOUND:\nDB_HOST={server}\nODBC_DRIVER={driver}")
            conn.close()
            exit(0)
        except Exception as e:
            print(f" FAIL ({str(e).split(']')[0]})") # Short error
