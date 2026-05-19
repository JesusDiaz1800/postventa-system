#!/usr/bin/env python
"""
Script para saltar migraciones problemáticas y aplicar solo las existentes
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== SALTAR MIGRACIONES PROBLEMATICAS ===")
    
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
        
        # Aplicar solo migraciones existentes
        print("\n[1/2] Aplicando migraciones existentes...")
        call_command('migrate', verbosity=1)
        
        # Verificar estado final
        print("\n[2/2] Verificando estado final...")
        from io import StringIO
        out = StringIO()
        call_command('showmigrations', stdout=out)
        final_output = out.getvalue()
        
        print("Estado final de migraciones:")
        print(final_output)
        
        # Verificar si hay migraciones pendientes
        if "[ ]" in final_output:
            print("\n⚠ ADVERTENCIA: Hay migraciones pendientes")
            print("  Esto es normal si hay cambios en los modelos")
            print("  El sistema funcionará con las migraciones aplicadas")
        else:
            print("\n✓ Todas las migraciones están aplicadas")
        
        print("\n✓ Proceso completado")
        print("\n📝 NOTA: Si hay migraciones pendientes, el sistema funcionará")
        print("   pero algunos campos nuevos no estarán disponibles en la BD")
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
