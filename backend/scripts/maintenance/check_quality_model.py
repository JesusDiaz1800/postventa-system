#!/usr/bin/env python
"""
Script para verificar el modelo QualityReport
"""
import os
import sys
import django

def main():
    print("=== VERIFICACION DEL MODELO QUALITYREPORT ===")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
    
    try:
        django.setup()
        print("✓ Django configurado correctamente")
    except Exception as e:
        print(f"✗ Error configurando Django: {e}")
        return False
    
    try:
        # Importar el modelo
        from apps.documents.models import QualityReport
        print("✓ Modelo QualityReport importado correctamente")
        
        # Verificar campos
        fields = QualityReport._meta.get_fields()
        print(f"✓ Modelo tiene {len(fields)} campos")
        
        # Verificar choices
        report_type_field = QualityReport._meta.get_field('report_type')
        choices = report_type_field.choices
        print(f"✓ Choices de report_type: {choices}")
        
        # Verificar constraints
        constraints = QualityReport._meta.constraints
        print(f"✓ Constraints: {len(constraints)}")
        
        # Verificar si la tabla existe en la base de datos
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quality_reports';")
            table_exists = cursor.fetchone()
            
        if table_exists:
            print("✓ Tabla 'quality_reports' existe en la base de datos")
        else:
            print("⚠ Tabla 'quality_reports' NO existe en la base de datos")
            print("  Esto indica que la migración no se ha aplicado")
        
        print("\n✓ Modelo QualityReport está funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error con el modelo QualityReport: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n=== MODELO OK ===")
    else:
        print("\n=== ERROR EN MODELO ===")
    
    input("\nPresiona Enter para continuar...")
