#!/usr/bin/env python
"""
Script para corregir problemas de migraciones
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== CORRECCION DE MIGRACIONES ===")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    
    try:
        django.setup()
        print("✓ Django configurado correctamente")
    except Exception as e:
        print(f"✗ Error configurando Django: {e}")
        return False
    
    try:
        # Verificar estado de migraciones
        print("\n[1/3] Verificando estado de migraciones...")
        from django.core.management import call_command
        from io import StringIO
        
        # Capturar salida de showmigrations
        out = StringIO()
        call_command('showmigrations', stdout=out)
        migrations_output = out.getvalue()
        
        print("Estado de migraciones:")
        print(migrations_output)
        
        # Crear migraciones
        print("\n[2/3] Creando migraciones...")
        call_command('makemigrations', 'documents', verbosity=2)
        call_command('makemigrations', 'audit', verbosity=2)
        call_command('makemigrations', 'incidents', verbosity=2)
        call_command('makemigrations', verbosity=2)
        
        # Aplicar migraciones
        print("\n[3/3] Aplicando migraciones...")
        call_command('migrate', verbosity=2)
        
        print("\n✓ Migraciones corregidas exitosamente")
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
