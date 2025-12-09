#!/usr/bin/env python
"""
Script directo para verificar y corregir migraciones en SQL Server
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== VERIFICACION Y CORRECCION DIRECTA ===")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    
    try:
        import django
        django.setup()
        print("✓ Django configurado correctamente")
    except Exception as e:
        print(f"✗ Error configurando Django: {e}")
        return False
    
    try:
        from django.db import connection
        
        print("\n[1/3] Verificando tablas existentes...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME IN ('incidents_incident', 'incidents_incidenttimeline', 'audit_logs', 'quality_reports')
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                print(f"  Tablas existentes: {existing_tables}")
                
                # Verificar tablas críticas
                if 'incidents_incident' in existing_tables:
                    print("✓ Tabla incidents_incident existe")
                else:
                    print("⚠ Tabla incidents_incident NO existe")
                
                if 'incidents_incidenttimeline' in existing_tables:
                    print("✓ Tabla incidents_incidenttimeline existe")
                else:
                    print("⚠ Tabla incidents_incidenttimeline NO existe")
                    
        except Exception as e:
            print(f"⚠ Error verificando tablas: {e}")
        
        print("\n[2/3] Aplicando migraciones existentes...")
        try:
            from django.core.management import call_command
            call_command('migrate', verbosity=1)
            print("✓ Migraciones aplicadas")
        except Exception as e:
            print(f"⚠ Error aplicando migraciones: {e}")
        
        print("\n[3/3] Verificando estado final...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME IN ('incidents_incident', 'incidents_incidenttimeline', 'audit_logs', 'quality_reports')
                """)
                final_tables = [row[0] for row in cursor.fetchall()]
                print(f"  Tablas finales: {final_tables}")
                
                # Verificar tablas críticas
                if 'incidents_incident' in final_tables:
                    print("✓ Tabla incidents_incident disponible")
                else:
                    print("⚠ Tabla incidents_incident NO disponible")
                
                if 'incidents_incidenttimeline' in final_tables:
                    print("✓ Tabla incidents_incidenttimeline disponible")
                else:
                    print("⚠ Tabla incidents_incidenttimeline NO disponible")
                    
        except Exception as e:
            print(f"⚠ Error verificando estado final: {e}")
        
        print("\n✓ Verificación completada")
        return True
        
    except Exception as e:
        print(f"✗ Error en verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n=== VERIFICACION COMPLETADA ===")
    else:
        print("\n=== ERROR - REVISAR LOGS ===")
    
    input("\nPresiona Enter para continuar...")
