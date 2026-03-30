
import os
import django
import sys

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.documents.models import VisitReport
from apps.documents.services.report_sync_service import ReportSyncService

class MockSAPTx:
    def __init__(self):
        self.last_payload = None
    def update_service_call(self, call_id, payload):
        self.last_payload = payload
        print(f"MOCK SAP: Updating SC {call_id} with payload: {payload}")

def test_payload():
    report_id = 20269 # Usar el reporte verificado anteriormente (RV-2026-076)
    try:
        report = VisitReport.objects.get(id=report_id)
        mock_sap = MockSAPTx()
        
        print(f"Testing UDF update for Report {report.report_number}")
        print(f"Related Incident: {report.related_incident.code}")
        print(f"Incident Category: {report.related_incident.categoria.name if report.related_incident.categoria else 'None'}")
        print(f"Incident Subcategory: {report.related_incident.subcategoria}")
        
        # Call the private method (testing logic)
        ReportSyncService._update_sap_udfs(report, 26710, mock_sap)
        
        payload = mock_sap.last_payload
        if payload and 'U_is_categoria' in payload and 'U_is_subcategoria' in payload:
            print("SUCCESS: Category UDFs found in payload.")
            print(f"U_is_categoria: {payload['U_is_categoria']}")
            print(f"U_is_subcategoria: {payload['U_is_subcategoria']}")
        else:
            print("FAILED: Category UDFs missing from payload.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_payload()
