import os
import requests
import json
from django.conf import settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_attachment_upload():
    print("--- Testing SAP Service Layer Attachments2 (Shell Mode) ---")
    
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
    filename = "test_attachment_sap_shell.txt"
    with open(filename, "w") as f:
        f.write("This is a test attachment from the Postventa System integration (Shell).")

    # 4. Upload to Attachments2
    url = f"{base_url}/Attachments2"
    
    files = {
        'files': (filename, open(filename, 'rb'), 'text/plain')
    }
    
    try:
        print(f"Uploading {filename} to {url}...")
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
                "CustomerCode": "C10198172-K", 
                "Subject": "Test Attachment Integration Shell",
                "Description": "Testing attachment link via Shell.",
                "Priority": "scp_Low",
                "Origin": -1,
                "Status": -3,
                "AttachmentEntry": abs_entry
            }
            
            sc_url = f"{base_url}/ServiceCalls"
            sc_res = requests.post(sc_url, json=sc_payload, cookies=cookies, verify=False)
            
            print(f"Service Call Status: {sc_res.status_code}")
            print(f"Service Call Response: {sc_res.text}")
            
            if sc_res.status_code in [200, 201]:
                sc_data = sc_res.json()
                sc_id = sc_data.get('ServiceCallID')
                print(f"Created Service Call: {sc_id}")
                
                # 6. Test ADDING another file to the SAME Service Call
                # Strategy: Create NEW Attachment with BOTH files? Or PATCH Attachment?
                # SAP SL Attachments2 PATCH usually allows adding lines.
                # Let's try to upload a SECOND file to a NEW AttachmentEntry and Update the SC?
                # Or PATCH the existing AttachmentEntry?
                
                print("--- Testing Update/Append Strategy ---")
                filename2 = "test_update.txt"
                with open(filename2, "w") as f2:
                    f2.write("Second file.")
                
                # Try PATCH to Attachments2(abs_entry)
                patch_url = f"{base_url}/Attachments2({abs_entry})"
                files2 = {'files': (filename2, open(filename2, 'rb'), 'text/plain')}
                
                print(f"Attempting PATCH to {patch_url}...")
                patch_res = requests.patch(patch_url, files=files2, cookies=cookies, verify=False)
                print(f"PATCH Status: {patch_res.status_code}")
                # PATCH usually returns 204 No Content on success
                
                if patch_res.status_code == 204:
                    print("PATCH successful! File added to existing attachment.")
                else:
                    print(f"PATCH failed: {patch_res.text}")
                    # If PATCH fails, we might need to POST new and Update SC.
            
        else:
            print("Upload failed.")

    except Exception as e:
        print(f"Exception: {e}")
    finally:
        if os.path.exists(filename):
            try: os.remove(filename)
            except: pass
        if os.path.exists("test_update.txt"):
            try: os.remove("test_update.txt")
            except: pass

test_attachment_upload()
