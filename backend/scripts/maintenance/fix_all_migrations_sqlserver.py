#!/usr/bin/env python
"""
Script completo para corregir todas las migraciones en SQL Server Express
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== CORRECCION COMPLETA DE MIGRACIONES (SQL SERVER) ===")
    
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
        from django.core.management import call_command
        from django.db import connection
        
        print("\n[1/6] Verificando conexión a SQL Server...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                print(f"✓ Conectado a SQL Server: {version[:50]}...")
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            return False
        
        print("\n[2/6] Verificando tablas existentes...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME IN ('incidents_incident', 'incidents_incidenttimeline', 'audit_logs', 'quality_reports')
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                print(f"  Tablas existentes: {existing_tables}")
        except Exception as e:
            print(f"⚠ Error verificando tablas: {e}")
        
        print("\n[3/6] Creando migraciones faltantes...")
        try:
            # Crear migraciones para cada app
            print("  → Creando migraciones para incidents...")
            call_command('makemigrations', 'incidents', verbosity=1)
            
            print("  → Creando migraciones para audit...")
            call_command('makemigrations', 'audit', verbosity=1)
            
            print("  → Creando migraciones para documents...")
            call_command('makemigrations', 'documents', verbosity=1)
            
            print("  → Creando migraciones generales...")
            call_command('makemigrations', verbosity=1)
            
            print("✓ Migraciones creadas exitosamente")
        except Exception as e:
            print(f"⚠ Error creando migraciones: {e}")
            print("  Continuando con migraciones existentes...")
        
        print("\n[4/6] Aplicando migraciones...")
        try:
            call_command('migrate', verbosity=1)
            print("✓ Migraciones aplicadas exitosamente")
        except Exception as e:
            print(f"⚠ Error aplicando migraciones: {e}")
            print("  Intentando aplicar migraciones específicas...")
            
            # Intentar aplicar migraciones específicas
            try:
                call_command('migrate', 'incidents', verbosity=1)
                call_command('migrate', 'audit', verbosity=1)
                call_command('migrate', 'documents', verbosity=1)
                print("✓ Migraciones específicas aplicadas")
            except Exception as e2:
                print(f"⚠ Error en migraciones específicas: {e2}")
        
        print("\n[5/6] Verificando tablas creadas...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME IN ('incidents_incident', 'incidents_incidenttimeline', 'audit_logs', 'quality_reports')
                """)
                final_tables = [row[0] for row in cursor.fetchall()]
                print(f"  Tablas finales: {final_tables}")
                
                # Verificar campos específicos
                if 'incidents_incident' in final_tables:
                    print("✓ Tabla incidents_incident creada")
                else:
                    print("⚠ Tabla incidents_incident NO creada")
                
                if 'incidents_incidenttimeline' in final_tables:
                    print("✓ Tabla incidents_incidenttimeline creada")
                else:
                    print("⚠ Tabla incidents_incidenttimeline NO creada")
                    
        except Exception as e:
            print(f"⚠ Error verificando tablas: {e}")
        
        print("\n[6/6] Verificando estado final...")
        try:
            from io import StringIO
            out = StringIO()
            call_command('showmigrations', stdout=out)
            final_output = out.getvalue()
            
            # Verificar si hay migraciones pendientes
            if "[ ]" in final_output:
                print("⚠ ADVERTENCIA: Aún hay migraciones pendientes")
                print("  Revisar manualmente: python manage.py makemigrations")
            else:
                print("✓ Todas las migraciones están aplicadas")
                
        except Exception as e:
            print(f"⚠ Error verificando estado: {e}")
        
        print("\n✓ Proceso completado")
        return True
        
    except Exception as e:
        print(f"✗ Error en migraciones: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n=== SISTEMA CORREGIDO ===")
    else:
        print("\n=== ERROR - REVISAR LOGS ===")
    
    input("\nPresiona Enter para continuar...")
