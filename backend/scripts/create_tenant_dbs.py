import pyodbc
import os
import sys
import time

# Configuración (Hardcoded según settings.py para asegurar funcionamiento)
# Intentar leer .env manualmente si os.getenv falla o si se ejecuta fuera de contexto
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = os.getenv('DB_HOST', '192.168.1.232') # Default to known correct IP
USER = os.getenv('DB_USER', 'ccalidad')
PASSWORD = os.getenv('DB_PASSWORD', 'Plf2025**')
DRIVER = '{ODBC Driver 13 for SQL Server}' # Confirmed installed

def create_database(cursor, db_name):
    """Crea una base de datos si no existe."""
    print(f"Creating database '{db_name}'...")
    try:
        # Check if DB exists
        cursor.execute(f"SELECT database_id FROM sys.databases WHERE Name = '{db_name}'")
        if cursor.fetchone():
            print(f"Database '{db_name}' already exists.")
            return

        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully.")
        
    except Exception as e:
        print(f"Error creating '{db_name}': {e}")

def main():
    print("--- Multi-Country Database Generator ---")
    
    # Debug connection info
    print(f"Connecting to: {SERVER}")
    print(f"User: {USER}")
    print(f"Driver: {DRIVER}")
    
    conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={PASSWORD};TrustServerCertificate=yes;Encrypt=no;App=MultiTenantSetup'
    
    try:
        # Conectar a master para crear DBs
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        databases = ['PRDPOSTVENTA_PE', 'PRDPOSTVENTA_CO']
        
        for db in databases:
            create_database(cursor, db)
            
        print("\n--- Process Finished ---")
        print("Now you can run migrations:")
        print("python manage.py migrate --database=default_pe")
        print("python manage.py migrate --database=default_co")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Could not connect to SQL Server: {e}")
        print("Verifique que el servicio SQL Server esté corriendo y las credenciales sean correctas.")

if __name__ == "__main__":
    main()
