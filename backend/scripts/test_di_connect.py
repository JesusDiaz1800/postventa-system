import win32com.client
import sys

# SAP Credentials
SAP_SERVER = "PLFSCL0VIR010"
SAP_COMPANY_DB = "PRDPOLIFUSION"
SAP_USER = "ccalidad"
SAP_PASSWORD = "Plf5647**"

# DB Type: 
# dst_MSSQL2012 = 7
# dst_MSSQL2014 = 8
# dst_MSSQL2016 = 9
# dst_MSSQL2017 = 10
# dst_MSSQL2019 = 11? 
# Use 10 or 8 is common safe bet, or let it guess? No, needed.
# Let's try 10 (2017) or 11 (2019). The system is 10.0 FP 2202, so likely SQL 2017/2019.
DST_MSSQL2016 = 9
DST_MSSQL2017 = 10

def test_connection():
    try:
        company = win32com.client.Dispatch("SAPbobsCOM.Company")
        
        company.Server = SAP_SERVER
        company.CompanyDB = SAP_COMPANY_DB
        company.UserName = SAP_USER
        company.Password = SAP_PASSWORD
        company.DbServerType = DST_MSSQL2017 
        
        # Try Trusted Authentication first (Single Sign On)
        company.UseTrusted = True 
        
        print(f"Attempting to connect to {SAP_SERVER} / {SAP_COMPANY_DB} with User {SAP_USER} (Trusted)...")
        
        ret = company.Connect()
        
        if ret == 0:
            print("✅ Connected SUCCESSFULLY!")
            print(f"Company Name: {company.CompanyName}")
            company.Disconnect()
        else:
            err_code, err_msg = company.GetLastError()
            print(f"Connection Failed: {err_code} - {err_msg}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()
