#!/usr/bin/env python
"""
Script automático para corregir migraciones con respuestas predefinidas
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    print("=== CORRECCION AUTOMATICA DE MIGRACIONES ===")
    
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
        
        # Configurar respuestas automáticas
        import django.db.migrations.questioner
        original_ask_rename = django.db.migrations.questioner.MigrationQuestioner.ask_rename
        
        def auto_ask_rename(self, model_name, old_name, new_name, field):
            print(f"  → Campo renombrado: {old_name} → {new_name} en {model_name}")
            return False  # No es un rename, es un campo nuevo
        
        django.db.migrations.questioner.MigrationQuestioner.ask_rename = auto_ask_rename
        
        try:
            # Crear migraciones para cada app
            print("\n[1/3] Creando migraciones para audit...")
            call_command('makemigrations', 'audit', verbosity=1)
            print("✓ Migraciones de audit creadas")
            
            print("\n[2/3] Creando migraciones para documents...")
            call_command('makemigrations', 'documents', verbosity=1)
            print("✓ Migraciones de documents creadas")
            
            print("\n[3/3] Creando migraciones para incidents...")
            call_command('makemigrations', 'incidents', verbosity=1)
            print("✓ Migraciones de incidents creadas")
            
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
            
        finally:
            # Restaurar función original
            django.db.migrations.questioner.MigrationQuestioner.ask_rename = original_ask_rename
        
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
