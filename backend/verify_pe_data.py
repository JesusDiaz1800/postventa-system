import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections
from apps.core.thread_local import set_current_country

def verify_data():
    set_current_country('PE')
    card_code = "CL20101095747"
    print(f"Buscando Cliente {card_code} en OCRD (PE)...")
    try:
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT CardCode, CardName, CardType FROM OCRD WHERE CardCode = %s", [card_code])
            res = cursor.fetchone()
            if res:
                print(f"Encontrado: {res}")
            else:
                print("¡ERROR! Cliente no encontrado en PE.")
                
        print("\nListando Series para OSCL (PE)...")
        with connections['sap_db_pe'].cursor() as cursor:
            cursor.execute("SELECT Series, SeriesName FROM NNM1 WHERE ObjectCode = '191'")
            for row in cursor.fetchall():
                print(f"Series OSCL: {row}")
                
        print("\nVerificando si el técnico 1 tiene el rol de técnico (T1)...")
        # En SAP OSCL, el assignee debe estar en la lista de empleados.
        # Pero a veces se requiere que el empleado esté vinculado a un rol.
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_data()
