import win32com.client
import sys

# SAP Credentials
SAP_SERVER = "PLFSCL0VIR010"
SAP_COMPANY_DB = "PRDPOLIFUSION"
SAP_USER = "ccalidad"
SAP_PASSWORD = "Plf5647**"
SAP_DB_USER = "sa" # Assuming SQL Auth, might need adjustment or Trusted
SAP_DB_PASSWORD = "..." # We don't have SA password, but maybe Trusted works?

# DI API typically needs:
# Server, CompanyDB, DbServerType, DbUserName, DbPassword, UserName, Password

def check_di_api():
    print("Initializing SAPbobsCOM.Company...")
    try:
        company = win32com.client.Dispatch("SAPbobsCOM.Company")
        print("DI API COM Object created successfully!")
    except Exception as e:
        print(f"Failed to load DI API: {e}")
        return

    # Info
    print(f"DI API Version: {company.GetVersion()}")
    
    # We won't try to Connect yet because we might lack DB credentials (sa).
    # But just loading the COM object proves it is installed.
    # The User/Pass provided (ccalidad) is for SAP B1, but Connect() also needs DB User/Pass usually unless using Windows Auth (Trusted).
    
    print("DI API is installed and accessible via Python.")

if __name__ == "__main__":
    check_di_api()
