import os
import django
import sys
import threading
import time

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import get_current_country, set_current_country, clear_current_country

def test_context():
    def check_it(expected):
        actual = get_current_country()
        print(f"Inside Thread: Expected={expected}, Actual={actual}")

    # SIMULATE SIGNAL wrapping logic
    for country_code in ['CL', 'CO', 'PE']:
        set_current_country(country_code)
        
        # This is what I implemented in signals.py
        current = get_current_country()
        def wrapper():
            set_current_country(current)
            try:
                check_it(country_code)
            finally:
                clear_current_country()
        
        t = threading.Thread(target=wrapper)
        t.start()
        t.join()
        clear_current_country()

if __name__ == "__main__":
    test_context()
