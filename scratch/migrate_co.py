import sys
import os
import django
from django.core.management import call_command

sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

print("Applying migrations to default_co (Colombia App DB)...")
try:
    call_command('migrate', database='default_co')
    print("Migraciones aplicadas correctamente.")
except Exception as e:
    print(f"Error applying migrations: {e}")
