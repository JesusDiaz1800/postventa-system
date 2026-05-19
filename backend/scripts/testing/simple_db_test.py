#!/usr/bin/env python3
"""
Script simple para probar la conexión a SQL Server
"""

import pyodbc
import sys

def test_sql_connection():
    """Test SQL Server connection with Windows Authentication"""
    print("🔍 Probando conexión a SQL Server...")
    print("=" * 50)
    
    # Configuration
    host = "localhost"
    port = "62161"
    instance = "SQLEXPRESS"
    database = "postventa_system"
    
    print(f"Host: {host}")
    print(f"Puerto: {port}")
    print(f"Instancia: {instance}")
    print(f"Base de datos: {database}")
    print(f"Autenticación: Windows")
    print()
    
    try:
        # Connection string for Windows Authentication
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host}\\{instance},{port};Trusted_Connection=yes;"
        
        print("🔗 Intentando conectar...")
        conn = pyodbc.connect(connection_string, timeout=10)
        print("✅ ¡Conexión exitosa!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print(f"✅ Versión de SQL Server: {version[0][:100]}...")
        
        # Check if database exists
        cursor.execute("SELECT name FROM sys.databases WHERE name = ?", database)
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"✅ Base de datos '{database}' encontrada!")
        else:
            print(f"⚠️  Base de datos '{database}' no existe. Se creará automáticamente.")
        
        # Close connection
        conn.close()
        print("✅ Conexión cerrada correctamente")
        
        print("\n" + "=" * 50)
        print("🎉 ¡CONEXIÓN EXITOSA!")
        print("\n📋 Configuración confirmada:")
        print(f"   Host: {host}")
        print(f"   Puerto: {port}")
        print(f"   Instancia: {instance}")
        print(f"   Autenticación: Windows")
        print(f"   Base de datos: {database}")
        
        return True
        
    except pyodbc.Error as e:
        print(f"❌ Error de conexión: {e}")
        print("\n🔧 Posibles soluciones:")
        print("1. Verificar que SQL Server esté ejecutándose")
        print("2. Verificar que el puerto 62161 esté abierto")
        print("3. Verificar que TCP/IP esté habilitado")
        print("4. Verificar firewall")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Main function"""
    print("🚀 PRUEBA DE CONEXIÓN SQL SERVER")
    print("=" * 60)
    
    success = test_sql_connection()
    
    if success:
        print("\n🚀 Próximos pasos:")
        print("1. Instalar dependencias: pip install -r requirements-sqlserver.txt")
        print("2. Ejecutar migraciones: python manage.py migrate")
        print("3. Crear superusuario: python manage.py createsuperuser")
        print("4. Iniciar servidor: python manage.py runserver")
    else:
        print("\n❌ Revisa la configuración y vuelve a intentar")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
