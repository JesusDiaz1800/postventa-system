#!/usr/bin/env python
"""
Script final para corregir migraciones pendientes
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== CORRECCION FINAL DE MIGRACIONES ===")
    
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
        
        # Crear migraciones para cada app específicamente
        print("\n[1/3] Creando migraciones para audit...")
        try:
            call_command('makemigrations', 'audit', verbosity=1)
            print("✓ Migraciones de audit creadas")
        except Exception as e:
            print(f"⚠ Error en audit: {e}")
        
        print("\n[2/3] Creando migraciones para documents...")
        try:
            call_command('makemigrations', 'documents', verbosity=1)
            print("✓ Migraciones de documents creadas")
        except Exception as e:
            print(f"⚠ Error en documents: {e}")
        
        print("\n[3/3] Creando migraciones para incidents...")
        try:
            call_command('makemigrations', 'incidents', verbosity=1)
            print("✓ Migraciones de incidents creadas")
        except Exception as e:
            print(f"⚠ Error en incidents: {e}")
        
        # Aplicar todas las migraciones
        print("\n[Aplicando migraciones...]")
        call_command('migrate', verbosity=1)
        
        # Verificar estado final
        print("\n[Verificando estado final...]")
        from io import StringIO
        out = StringIO()
        call_command('showmigrations', stdout=out)
        final_output = out.getvalue()
        
        # Verificar si hay migraciones pendientes
        if "[ ]" in final_output:
            print("\n⚠ ADVERTENCIA: Aún hay migraciones pendientes")
            print("  Revisar manualmente: python manage.py makemigrations")
        else:
            print("\n✓ Todas las migraciones están aplicadas")
        
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
        print("\n=== SISTEMA LISTO ===")
    else:
        print("\n=== ERROR - REVISAR LOGS ===")
    
    input("\nPresiona Enter para continuar...")
