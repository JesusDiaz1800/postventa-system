import os
import sys
import django
import logging

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.sap_integration.sap_query_service import SAPQueryService

# Setup logging to console
logging.basicConfig(level=logging.INFO)

def verify_multi_upload():
    print("--- Starting Multi-File Upload Verification ---")
    
    svc = SAPTransactionService()
    query = SAPQueryService()
    
    # Use incident INC-2026-0028 (SAP ID 26716) - Chile
    call_id = 26716
    
    files_to_upload = [
        ("image_test_1.jpg", "Fake Image 1 Content"),
        ("image_test_2.jpg", "Fake Image 2 Content"),
        ("report_test.pdf", "Fake PDF Content")
    ]
    
    created_files = []
    
    try:
        for filename, content in files_to_upload:
            # Create dummy file
            fpath = os.path.join(os.getcwd(), filename)
            with open(fpath, "w") as f: f.write(content)
            created_files.append(fpath)
            
            print(f"\n>> Uploading {filename} to SAP (SC {call_id})...")
            res = svc.upload_attachment_to_service_call(call_id, fpath, filename)
            print(f"Result: {res}")
            
            if not res.get('success'):
                print(f"FAILED to upload {filename}: {res.get('error')}")
                # Don't break, try next
                
        # Final verification
        print("\n--- Final Verification in SAP ---")
        attachments = query.get_attachments(call_id)
        print(f"Total attachments linked to SC {call_id}: {len(attachments)}")
        
        for att in attachments:
            print(f" - Filename: {att.get('filename')} | Line: {att.get('line')}")
            
    finally:
        # Cleanup local files
        for f in created_files:
            if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    verify_multi_upload()
