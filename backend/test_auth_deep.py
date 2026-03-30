
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up django: {e}")

from django.contrib.auth import authenticate
from apps.core.thread_local import set_current_country, get_current_country
from django.db import connections

def test_auth():
    print("--- Detailed Auth Test ---")
    username = 'jdiaz'
    password = 'Plf2025**' # Correct password from test_e2e_sap.py
    
    # Test for each country
    for country in ['CL', 'PE', 'CO']:
        print(f"\nTesting with Country: {country}")
        set_current_country(country)
        print(f"Current country in thread: {get_current_country()}")
        
        # Check if DB is reachable
        from django.contrib.auth import get_user_model
        User = get_user_model()
        db = connections['default'] # This might be routed
        # Let's see what DB Django thinks it should use
        from django.db import router
        target_db = router.db_for_read(User)
        print(f"Django decided DB for User: {target_db}")
        
        try:
            user_exists = User.objects.using(target_db).filter(username=username).exists()
            print(f"User '{username}' exists in {target_db}? {user_exists}")
            
            if user_exists:
                user = authenticate(None, username=username, password=password)
                if user:
                    print(f"SUCCESS: Authenticated {username} in {country} Context!")
                else:
                    print(f"FAILED: authenticate() returned None for {username} in {country} Context.")
                    # Try to check password manually
                    u = User.objects.using(target_db).get(username=username)
                    pwd_ok = u.check_password(password)
                    print(f"Manual check_password('{password}'): {pwd_ok}")
        except Exception as e:
            print(f"Error during test for {country}: {e}")

if __name__ == "__main__":
    test_auth()
