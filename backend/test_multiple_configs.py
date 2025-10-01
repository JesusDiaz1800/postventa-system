#!/usr/bin/env python3
"""
Script para probar diferentes configuraciones de conexión
"""

import pyodbc
import sys

def test_connection(host, port, instance, description):
    """Test a specific connection configuration"""
    print(f"\n🔍 Probando: {description}")
    print(f"   Host: {host}, Puerto: {port}, Instancia: {instance}")
    
    try:
        # Different connection string formats
        connection_strings = [
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host}\\{instance},{port};Trusted_Connection=yes;",
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};Trusted_Connection=yes;",
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host}\\{instance};Trusted_Connection=yes;",
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};Trusted_Connection=yes;",
        ]
        
        for i, conn_str in enumerate(connection_strings, 1):
            try:
                print(f"   Intento {i}: {conn_str[:80]}...")
                conn = pyodbc.connect(conn_str, timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()
                conn.close()
                print(f"   ✅ ¡ÉXITO! Versión: {version[0][:50]}...")
                return True, conn_str
            except Exception as e:
                print(f"   ❌ Falló: {str(e)[:60]}...")
                continue
        
        return False, None
        
    except Exception as e:
        print(f"   ❌ Error general: {e}")
        return False, None

def main():
    """Main function"""
    print("🚀 PRUEBA DE MÚLTIPLES CONFIGURACIONES")
    print("=" * 60)
    
    # Test configurations
    configs = [
        ("192.168.1.161", "62161", "SQLEXPRESS", "Configuración original"),
        ("192.168.1.161", "1433", "SQLEXPRESS", "Puerto estándar 1433"),
        ("192.168.1.161", "1434", "SQLEXPRESS", "Puerto alternativo 1434"),
        ("localhost", "62161", "SQLEXPRESS", "Localhost con puerto dinámico"),
        ("localhost", "1433", "SQLEXPRESS", "Localhost puerto estándar"),
        ("127.0.0.1", "62161", "SQLEXPRESS", "127.0.0.1 con puerto dinámico"),
        ("127.0.0.1", "1433", "SQLEXPRESS", "127.0.0.1 puerto estándar"),
    ]
    
    successful_configs = []
    
    for host, port, instance, description in configs:
        success, conn_str = test_connection(host, port, instance, description)
        if success:
            successful_configs.append((host, port, instance, conn_str, description))
    
    print("\n" + "=" * 60)
    if successful_configs:
        print("🎉 ¡CONFIGURACIONES EXITOSAS ENCONTRADAS!")
        print("\n📋 Configuraciones que funcionan:")
        for i, (host, port, instance, conn_str, description) in enumerate(successful_configs, 1):
            print(f"\n{i}. {description}")
            print(f"   Host: {host}")
            print(f"   Puerto: {port}")
            print(f"   Instancia: {instance}")
            print(f"   Connection String: {conn_str}")
        
        print(f"\n🔧 Para usar la primera configuración exitosa:")
        print(f"   Actualizar .env con:")
        print(f"   DB_HOST={successful_configs[0][0]}")
        print(f"   DB_PORT={successful_configs[0][1]}")
        
    else:
        print("❌ No se encontraron configuraciones exitosas")
        print("\n🔧 Posibles problemas:")
        print("1. SQL Server no está ejecutándose")
        print("2. Firewall bloquea las conexiones")
        print("3. SQL Server no está configurado para conexiones remotas")
        print("4. El puerto dinámico cambió")
        print("\n💡 Soluciones:")
        print("1. Verificar SQL Server Configuration Manager")
        print("2. Verificar Windows Firewall")
        print("3. Verificar que SQL Server Browser esté ejecutándose")
        print("4. Probar con SQL Server Management Studio")
    
    return len(successful_configs) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
