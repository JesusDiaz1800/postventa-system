import os
import django
import logging

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.sap_integration.sap_query_service import SAPQueryService
from apps.core.thread_local import set_current_country
from django.db import connections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_co_integration():
    set_current_country('CO')
    print("--- Verifying Colombia Integration ---")
    
    # 1. Check SQL Connection
    print("\n1. Checking SQL Connection to sap_db_co...")
    try:
        with connections['sap_db_co'].cursor() as cursor:
            cursor.execute("SELECT TOP 1 CardCode, CardName FROM OCRD")
            row = cursor.fetchone()
            if row:
                print(f"SQL Success! Found customer: {row[0]} - {row[1]}")
            else:
                print("SQL Success but no customers found.")
    except Exception as e:
        print(f"SQL Failed: {e}")
        return
    
    # 2. Check Service Layer Login
    print("\n2. Checking Service Layer Login for CO...")
    sap_tx = SAPTransactionService()
    if sap_tx._login():
        print(f"Service Layer Login Success! Connected to {sap_tx.company_db} as {sap_tx.user}")
    else:
        print("Service Layer Login Failed.")
        return

    # 3. List some technicians via Query Service
    print("\n3. Listing Technicians via SAPQueryService (CO)...")
    query_service = SAPQueryService()
    techs = query_service.get_technicians()
    for t in techs[:5]:
        print(f"Tech: {t['id']} - {t['name']}")

    # 4. Attempting to create a Test Service Call...
    print("\n4. Attempting to create a Test Service Call...")
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # Seleccionar un cliente ACTIVO
            cursor.execute("SELECT TOP 1 CardCode, CardName FROM OCRD WHERE CardType='C' AND frozenFor='N' AND (validFor='Y' OR validFor IS NULL)")
            cust_row = cursor.fetchone()
            if not cust_row:
                print("No active customers found to create a test service call.")
                return
            card_code = cust_row[0]
            print(f"Using active customer: {card_code} - {cust_row[1]}")
            
            res = sap_tx.create_service_call(
                customer_code=card_code,
                subject="TEST INTEGRATION COLOMBIA - IGNORE",
                description="Prueba de integración realizada por Antigravity.",
                technician_code=2  # Responsable
            )
            
            if res.get('success'):
                doc_num = res.get('doc_num')
                call_id = res.get('service_call_id')
                print(f"Service Call Created! DocNum: {doc_num}, CallID: {call_id}")
                
                # 5. Try to create a Visit Report Sync (Simulated)
                print("\n5. Attempting to sync a simulated Visit Report...")
                from apps.reports.models import VisitReport
                from django.utils import timezone
                
                # We need a dummy report object (we won't save it to our DB, just pass it to the service)
                class DummyReport:
                    def __init__(self, call_id):
                        self.sap_call_id = call_id
                        self.wall_observations = "Muros OK (CO Test)"
                        self.matrix_observations = "Matriz OK (CO Test)"
                        self.slab_observations = "Losa OK (CO Test)"
                        self.storage_observations = None
                        self.pre_assembled_observations = None
                        self.exterior_observations = None
                        self.general_observations = "Integración exitosa."
                        self.visit_date = timezone.now().date()
                        self.machine_data = {'machine_removal': False, 'machines': []}

                report = DummyReport(call_id)
                sync_res = sap_tx.update_service_call_from_visit_report(report)
                
                if sync_res.get('success'):
                    print("Visit Report Sync Success! UDFs updated in SAP.")
                else:
                    print(f"Visit Report Sync Failed: {sync_res.get('error')}")
            else:
                print(f"Service Call Creation Failed: {res.get('error')}")
    except Exception as e:
        print(f"Error during test creation: {e}")

if __name__ == "__main__":
    verify_co_integration()
