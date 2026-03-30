import os
import sys
import django
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Setup Django for settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.conf import settings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_sl_append():
    print("--- Testing SAP SL Attachments2 Append ---")
    
    # login via service
    from apps.sap_integration.sap_transaction_service import SAPTransactionService
    svc = SAPTransactionService()
    if not svc._login():
        print("Login failed via service")
        return
        
    base_url = svc.base_url
    cookies = svc.session_cookies
    print(f"Login successful to {svc.company_db}.")

    # 1. Create a NEW entry first (to ensure we have one)
    print("Step 1: Creating initial attachment...")
    f1 = "auto_test_1.txt"
    with open(f1, "w") as f: f.write("First file content")
    
    upload_url = f"{base_url}/Attachments2"
    res1 = requests.post(upload_url, files={'files': (f1, open(f1, 'rb'), 'text/plain')}, cookies=cookies, verify=False)
    
    if res1.status_code not in [200, 201]:
        print(f"Initial upload failed: {res1.text}")
        return
        
    abs_entry = res1.json().get('AbsoluteEntry')
    print(f"Initial AbsEntry: {abs_entry}")
    
    # 2. PATCH the existing entry with a SECOND file
    print(f"Step 2: PATCHing AbsEntry {abs_entry} with second file...")
    f2 = "auto_test_2.txt"
    with open(f2, "w") as f: f.write("Second file content")
    
    patch_url = f"{base_url}/Attachments2({abs_entry})"
    res2 = requests.patch(patch_url, files={'files': (f2, open(f2, 'rb'), 'text/plain')}, cookies=cookies, verify=False)
    
    print(f"PATCH Status: {res2.status_code}")
    if res2.status_code not in [200, 204]:
        print(f"PATCH failed: {res2.text}")
        
    # 3. Verify content
    print("Step 3: Verification...")
    res3 = requests.get(patch_url, cookies=cookies, verify=False)
    if res3.status_code == 200:
        data = res3.json()
        lines = data.get('Attachments2_Lines', [])
        print(f"Total lines in Attachments2({abs_entry}): {len(lines)}")
        for line in lines:
            print(f"  Line: {line.get('FileName')}.{line.get('FileExtension')}")
    else:
        print(f"GET failed: {res3.text}")

    # Cleanup
    for f in [f1, f2]:
        if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    test_sl_append()
