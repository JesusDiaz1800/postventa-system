import requests
import json
import urllib3

# Suppress SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration from User
SAP_SERVER = "192.168.1.237"
SAP_PORT = 50000
SAP_COMPANY_DB = "PRDPOLIFUSION"
SAP_USER = "ccalidad"
SAP_PASSWORD = "Plf5647**"

import socket

def resolve_host(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        print(f"DNS Resolution: {hostname} -> {ip}")
        return ip
    except Exception as e:
        print(f"DNS Resolution FAILED: {e}")
        return None

def check_connection():
    ip = resolve_host(SAP_SERVER)
    if not ip:
        print("Stopping due to DNS failure.")
        return

    # Try ports
    ports = [50000, 50001, 50002, 443]
    success = False
    
    for port in ports:
        base_url = f"https://{SAP_SERVER}:{port}/b1s/v1"
        login_url = f"{base_url}/Login"
        payload = {
            "CompanyDB": SAP_COMPANY_DB,
            "UserName": SAP_USER,
            "Password": SAP_PASSWORD
        }
        
        print(f"--- Testing Port {port} ---")
        try:
             # Timeout fast for discovery
            response = requests.post(
                login_url, 
                json=payload, 
                verify=False, 
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"[OK] Login SUCCESS on port {port}!")
                success = True
                break
            else:
                print(f"[FAIL] Port {port} reachable but Login Failed. Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                # If we got a response, the service is there, just auth failed
                success = True 
                break
                
        except requests.exceptions.ConnectionError:
            print(f"[Skip] Connection Refused on {port}")
        except Exception as e:
            print(f"[Error] {str(e)}")

    if not success:
        print("ALL PORTS FAILED.")

if __name__ == "__main__":
    check_connection()
