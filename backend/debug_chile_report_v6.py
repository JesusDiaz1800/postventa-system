import os
import django
import sys
import io

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.documents.models import VisitReport
from apps.incidents.models import Incident
from apps.sap_integration.sap_query_service import SAPQueryService

def check_everything():
    set_current_country('CL')
    reports = VisitReport.objects.all().order_by('-created_at')[:3]
    
    sap_query = SAPQueryService()

    for r in reports:
        print(f"\n--- REPORT {r.report_number} (ID: {r.id}) ---")
        print(f"Created: {r.created_at}")
        print(f"Sync Status: {r.sync_status}")
        print(f"PDF File: {r.pdf_file}")
        
        file_exists = False
        if r.pdf_file:
            try:
                file_exists = os.path.exists(r.pdf_file.path)
                print(f"File exists on disk: {file_exists} ({os.path.getsize(r.pdf_file.path)} bytes)")
            except Exception as e:
                print(f"Error checking disk file: {e}")

        # Check Incident
        inc = r.related_incident
        if inc:
            print(f"Incident: {inc.code} (Status: {inc.estado})")
            print(f"SAP DocNum: {inc.sap_doc_num}, SAP CallID: {inc.sap_call_id}")
            print(f"Closure Attachment: {inc.closure_attachment}")
            
            # Use sap_query to see attachments in SAP
            if inc.sap_doc_num:
                try:
                    print(f"Checking SAP Attachments for DocNum {inc.sap_doc_num}...")
                    sap_atts = sap_query.get_attachments(inc.sap_doc_num)
                    if sap_atts:
                        print(f"SAP Attachments found ({len(sap_atts)}):")
                        for sa in sap_atts:
                            print(f" - {sa.get('filename')} (Entry: {sa.get('atc_entry')})")
                    else:
                        print("NO ATTACHMENTS FOUND IN SAP!")
                except Exception as e:
                    print(f"Error querying SAP attachments: {e}")
        else:
            print("No related incident found.")

if __name__ == "__main__":
    check_everything()
