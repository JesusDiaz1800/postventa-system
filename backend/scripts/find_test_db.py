import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SAP_SERVER = "192.168.1.237"
SAP_PORT = 50000
SAP_USER = "ccalidad"
SAP_PASSWORD = "Plf5647**"

BASE_URL = f"https://{SAP_SERVER}:{SAP_PORT}/b1s/v1"

# Candidates based on "TEST POLIFUSION S.A."
CANDIDATES = [
    "TESTPOLIFUSION",
    "POLIFUSION_TEST",
    "PRDPOLIFUSION_TEST",
    "TEST_POLIFUSION",
    "SBODemoCL", # Common demo DB
    "PRDPOLIFUSION_RESPALDO",
    "SBO_POLIFUSION_TEST",
    "POLIFUSION_QA"
]

def try_login(company_db):
    try:
        response = requests.post(
            f"{BASE_URL}/Login",
            json={"CompanyDB": company_db, "UserName": SAP_USER, "Password": SAP_PASSWORD},
            verify=False,
            timeout=5
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, str(e)

def find_db():
    print(f"Searching for TEST database on {SAP_SERVER}...")
    
    for db in CANDIDATES:
        print(f"Trying {db}...", end=" ")
        success, details = try_login(db)
        if success:
            print("SUCCESS!")
            print(f"Found accessible database: {db}")
            print(f"SessionId: {details.get('SessionId')}")
            return db
        else:
            # Check if error is 'Invalid directory' (DB doesn't exist) vs 'Auth failed'
            err_code = details.get('error', {}).get('code') if isinstance(details, dict) else 'Unknown'
            print(f"Failed ({err_code})")
            
    print("No database found in candidate list.")
    return None

if __name__ == "__main__":
    find_db()
