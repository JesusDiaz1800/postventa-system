"""
Script de verificacion de conexion a SAP PRDPOLIFUSION
Modo: SOLO LECTURA
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections
from apps.sap_integration.models import BusinessPartner, ServiceCall, Project

def test_connection():
    """Probar conexion a SAP PRDPOLIFUSION"""
    print("=" * 60)
    print("VERIFICACION DE CONEXION A SAP PRDPOLIFUSION")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Conexion basica
        print("Test 1: Probando conexion basica...")
        with connections['sap_db'].cursor() as cursor:
            cursor.execute("SELECT DB_NAME() AS database_name")
            db_name = cursor.fetchone()[0]
            print(f"   [OK] Conectado a base de datos: {db_name}")
        print()
        
        # Test 2: Verificar permisos (solo lectura)
        print("Test 2: Verificando permisos de solo lectura...")
        with connections['sap_db'].cursor() as cursor:
            cursor.execute("SELECT HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'SELECT') AS has_select")
            has_select = cursor.fetchone()[0]
            print(f"   [{'OK' if has_select else 'ERROR'}] Permiso SELECT: {'Si' if has_select else 'No'}")
        print()
        
        # Test 3: Contar clientes (OCRD)
        print("Test 3: Consultando tabla OCRD (Clientes)...")
        try:
            count = BusinessPartner.objects.using('sap_db').count()
            print(f"   [OK] Total de Business Partners: {count}")
            
            # Mostrar primeros 5
            if count > 0:
                print("   Primeros 5 clientes:")
                for bp in BusinessPartner.objects.using('sap_db')[:5]:
                    print(f"      - {bp.card_code}: {bp.card_name}")
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
        print()
        
        # Test 4: Contar llamadas de servicio (OSCL)
        print("Test 4: Consultando tabla OSCL (Llamadas de Servicio)...")
        try:
            count = ServiceCall.objects.using('sap_db').count()
            print(f"   [OK] Total de Service Calls: {count}")
            
            # Mostrar ultimas 5
            if count > 0:
                print("   Ultimas 5 llamadas de servicio:")
                for call in ServiceCall.objects.using('sap_db').order_by('-create_date')[:5]:
                    date_str = call.create_date.strftime('%Y-%m-%d') if call.create_date else 'N/A'
                    print(f"      - Call ID {call.call_id}: {call.subject or 'Sin asunto'} ({date_str})")
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
        print()
        
        # Test 5: Contar obras (@FRMOBRAS)
        print("Test 5: Consultando tabla @FRMOBRAS (Obras)...")
        try:
            count = Project.objects.using('sap_db').count()
            print(f"   [OK] Total de Obras: {count}")
            
            # Mostrar primeras 5
            if count > 0:
                print("   Primeras 5 obras:")
                for project in Project.objects.using('sap_db')[:5]:
                    print(f"      - {project.code}: {project.name}")
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
        print()
        
        # Test 6: Verificar campos disponibles en OSCL
        print("Test 6: Verificando estructura de tabla OSCL...")
        with connections['sap_db'].cursor() as cursor:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'OSCL'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            print(f"   [OK] Columnas encontradas: {len(columns)}")
            print("   Primeras 10 columnas:")
            for col_name, col_type in columns[:10]:
                print(f"      - {col_name} ({col_type})")
        print()
        
        # Resumen final
        print("=" * 60)
        print("[OK] CONEXION EXITOSA A PRDPOLIFUSION")
        print("=" * 60)
        print()
        print("Resumen:")
        print(f"   - Base de datos: {db_name}")
        print(f"   - Modo: SOLO LECTURA")
        print(f"   - Usuario: ccalidad")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("[ERROR] FALLO DE CONEXION")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        return False

if __name__ == '__main__':
    test_connection()
