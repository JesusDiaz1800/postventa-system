import os
import sys
import django
import logging
import threading
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.sap_integration.sap_query_service import SAPQueryService

# Setup logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(threadName)s] %(message)s')

def upload_worker(svc, call_id, filename, content):
    fpath = os.path.join(os.getcwd(), filename)
    with open(fpath, "w") as f: f.write(content)
    
    try:
        print(f"Worker {filename} starting...")
        res = svc.upload_attachment_to_service_call(call_id, fpath, filename)
        print(f"Worker {filename} finished. Result: {res}")
    finally:
        if os.path.exists(fpath): os.remove(fpath)

def verify_concurrent_upload():
    print("--- Starting Concurrent Upload Verification ---")
    
    svc = SAPTransactionService()
    query = SAPQueryService()
    
    # Use incident INC-2026-0028 (SAP ID 26716) - Chile
    call_id = 26716
    
    threads = []
    for i in range(5):
        t = threading.Thread(
            target=upload_worker, 
            args=(svc, call_id, f"concurrent_{i}.jpg", f"Content {i}"),
            name=f"Thread-{i}"
        )
        threads.append(t)
        
    print("\n>> Launching 5 concurrent threads...")
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    # Final verification
    print("\n--- Final Verification in SAP ---")
    attachments = query.get_attachments(call_id)
    print(f"Total attachments linked to SC {call_id}: {len(attachments)}")
    
    for att in attachments:
        print(f" - Filename: {att.get('filename')}")

if __name__ == "__main__":
    verify_concurrent_upload()
