import os
import sys
import django
import requests
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_project.settings')
django.setup()

from django.conf import settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_attachment_upload():
    print("--- Testing SAP Service Layer Attachments2 ---")
    
    # 1. Config
    base_url = settings.SAP_SL_BASE_URL
    company_db = settings.SAP_SL_COMPANY_DB
    user = settings.SAP_SL_USER
    password = settings.SAP_SL_PASSWORD
    
    # 2. Login
    login_url = f"{base_url}/Login"
    payload = {"CompanyDB": company_db, "UserName": user, "Password": password}
    response = requests.post(login_url, json=payload, verify=False)
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
        
    cookies = response.cookies
    print("Login successful.")

    # 3. Create dummy file
    filename = "test_attachment_sap.txt"
    with open(filename, "w") as f:
        f.write("This is a test attachment from the Postventa System integration.")

    # 4. Upload to Attachments2
    url = f"{base_url}/Attachments2"
    
    # Prepare multipart
    files = {
        'files': (filename, open(filename, 'rb'), 'text/plain')
    }
    
    # NOTE: Requests handles multipart boundary automatically
    try:
        print(f"Uploading {filename} to {url}...")
        # Headers should NOT include Content-Type, requests adds it with boundary
        upload_res = requests.post(url, files=files, cookies=cookies, verify=False)
        
        print(f"Upload Status: {upload_res.status_code}")
        print(f"Upload Response: {upload_res.text}")
        
        if upload_res.status_code in [200, 201]:
            data = upload_res.json()
            abs_entry = data.get('AbsoluteEntry')
            print(f"SUCCESS! Attachment AbsoluteEntry: {abs_entry}")
            
            # 5. Create Service Call with Attachment
            print("Creating test Service Call with this attachment...")
            sc_payload = {
                "CustomerCode": "C10198172-K", # Ivan Michea
                "Subject": "Test Attachment Integration",
                "Description": "Testing attachment link.",
                "Priority": "scp_Low",
                "Origin": -1,
                "Status": -3,
                "AttachmentEntry": abs_entry # Link the attachment
            }
            
            sc_url = f"{base_url}/ServiceCalls"
            sc_res = requests.post(sc_url, json=sc_payload, cookies=cookies, verify=False)
            
            print(f"Service Call Status: {sc_res.status_code}")
            print(f"Service Call Response: {sc_res.text}")
            
        else:
            print("Upload failed.")

    except Exception as e:
        print(f"Exception: {e}")
    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    test_attachment_upload()
