import os
import sys
import django
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError

# Configure Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

def check_db(name):
    print(f"--- Checking Database: {name} ---")
    try:
        conn = connections[name]
        conn.cursor()
        print(f"[OK] Connection to '{name}' successful.")
        
        # Check migrations
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(conn)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if not plan:
            print(f"[OK] All migrations are up to date in '{name}'.")
        else:
            print(f"[WARN] Pending migrations in '{name}': {len(plan)}")
            for migration, backwards in plan:
                print(f"   - {migration}")
    except OperationalError as e:
        print(f"[FAIL] Connection to '{name}' FAILED: {e}")
    except Exception as e:
        print(f"[ERROR] Error checking '{name}': {e}")
    print()

def check_sap(country):
    print(f"--- Checking SAP Service Layer Config [{country}] ---")
    try:
        from apps.core.thread_local import set_current_country
        set_current_country(country)
        from apps.sap_integration.sap_transaction_service import SAPTransactionService
        service = SAPTransactionService()
        
        print(f"   Configured Company DB: {service.company_db}")
        print(f"   User: {service.user}")
        if service.password:
            print(f"   [OK] Password configured for {country}.")
        else:
            print(f"   [WARN] Password MISSING for {country}.")
        
        # We don't perform a live login call here to avoid 401s if the user hasn't put the keys yet,
        # but we validate the objects can be instantiated with the correct regional settings.
    except Exception as e:
        print(f"   [FAIL] SAP Config error for {country}: {e}")
    print()

def main():
    print("==================================================")
    print("   POSTVENTA SYSTEM - PRE-PRODUCTION CHECK")
    print("==================================================")
    print()
    
    # Check regional databases
    check_db('default')
    check_db('default_pe')
    check_db('default_co')
    
    # Check SAP config per country
    check_sap('CL')
    check_sap('PE')
    check_sap('CO')
    
    print("==================================================")
    print("   CHECK COMPLETED")
    print("==================================================")

if __name__ == "__main__":
    main()
