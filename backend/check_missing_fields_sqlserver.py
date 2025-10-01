#!/usr/bin/env python
"""
Script para verificar qué campos están faltando en SQL Server
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== VERIFICACION DE CAMPOS FALTANTES (SQL SERVER) ===")
    
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
        from apps.audit.models import AuditLog
        from apps.documents.models import QualityReport
        from apps.incidents.models import Incident, IncidentTimeline
        
        print("\n[1/4] Verificando modelo AuditLog...")
        try:
            # Verificar si la tabla existe
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'audit_logs'
                """)
                table_exists = cursor.fetchone()
                
            if table_exists:
                print("✓ Tabla audit_logs existe")
                
                # Verificar campos específicos
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'audit_logs'
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                print(f"  Campos en BD: {columns}")
                
                # Verificar si el campo 'details' existe
                if 'details' in columns:
                    print("✓ Campo 'details' existe en audit_logs")
                else:
                    print("⚠ Campo 'details' NO existe en audit_logs")
                    
                # Verificar si el campo 'description' existe (campo antiguo)
                if 'description' in columns:
                    print("⚠ Campo 'description' existe (campo antiguo)")
                else:
                    print("✓ Campo 'description' no existe (correcto)")
            else:
                print("✗ Tabla audit_logs NO existe")
                
        except Exception as e:
            print(f"⚠ Error verificando audit_logs: {e}")
        
        print("\n[2/4] Verificando modelo QualityReport...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'quality_reports'
                """)
                table_exists = cursor.fetchone()
                
            if table_exists:
                print("✓ Tabla quality_reports existe")
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'quality_reports'
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                print(f"  Campos en BD: {columns}")
                
                # Verificar campos específicos del QualityReport
                required_fields = ['report_number', 'report_type', 'related_incident_id', 'title', 'content']
                for field in required_fields:
                    if field in columns:
                        print(f"✓ Campo '{field}' existe")
                    else:
                        print(f"⚠ Campo '{field}' NO existe")
            else:
                print("✗ Tabla quality_reports NO existe")
                
        except Exception as e:
            print(f"⚠ Error verificando quality_reports: {e}")
        
        print("\n[3/4] Verificando modelo Incident...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'incidents_incident'
                """)
                table_exists = cursor.fetchone()
                
            if table_exists:
                print("✓ Tabla incidents_incident existe")
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'incidents_incident'
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                print(f"  Campos en BD: {len(columns)} campos")
                
                # Verificar campos específicos
                important_fields = ['created_by_id', 'assigned_to_id', 'closed_by_id', 'fecha_cierre', 'closed_at']
                for field in important_fields:
                    if field in columns:
                        print(f"✓ Campo '{field}' existe")
                    else:
                        print(f"⚠ Campo '{field}' NO existe")
            else:
                print("✗ Tabla incidents_incident NO existe")
                
        except Exception as e:
            print(f"⚠ Error verificando incidents_incident: {e}")
        
        print("\n[4/4] Verificando modelo IncidentTimeline...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'incidents_incidenttimeline'
                """)
                table_exists = cursor.fetchone()
                
            if table_exists:
                print("✓ Tabla incidents_incidenttimeline existe")
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'incidents_incidenttimeline'
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                print(f"  Campos en BD: {columns}")
            else:
                print("✗ Tabla incidents_incidenttimeline NO existe")
                
        except Exception as e:
            print(f"⚠ Error verificando incidents_incidenttimeline: {e}")
        
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
