import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
import django; django.setup()

from apps.core.thread_local import set_current_country
from apps.documents.models import VisitReport
from apps.documents.services.report_sync_service import ReportSyncService
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.sap_integration.sap_query_service import SAPQueryService

def test():
    set_current_country('PE')
    report = VisitReport.objects.filter(report_number="RV-2026-004").first()
    
    sap_tx = SAPTransactionService()
    sap_query = SAPQueryService()
    
    if not report:
        print("Reporte no encontrado")
        return
        
    print(f"Llamando a _update_sap_udfs para {report.report_number} con CallID={report.sap_call_id}")
    ReportSyncService._update_sap_udfs(report, report.sap_call_id, sap_tx, sap_query)
    print("Prueba finalizada.")

if __name__ == "__main__":
    test()
