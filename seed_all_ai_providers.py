import os
import django
import sys

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai_orchestrator.models import AIProvider
from django.conf import settings

def seed_providers_for_db(db_alias):
    print(f"--- Seeding AI Providers for database: {db_alias} ---")
    
    # 1. Google Gemini (Priority 1)
    google, created = AIProvider.objects.using(db_alias).get_or_create(
        name='google',
        defaults={
            'enabled': True,
            'priority': 1,
            'daily_quota_tokens': 500000,
            'daily_quota_calls': 2000,
        }
    )
    if not created:
        google.enabled = True
        google.priority = 1
        google.save(using=db_alias)
    
    # Use environment GEMINI_API_KEY if available and not already set
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and not google.api_key_encrypted:
        google.set_api_key(api_key)
        google.save(using=db_alias)
        print(f"  [OK] Google provider configured with API Key in {db_alias}")
    else:
        print(f"  [!] Google provider already exists in {db_alias}")

    # 2. Local Ollama (Priority 2 / Fallback)
    local, created = AIProvider.objects.using(db_alias).get_or_create(
        name='local',
        defaults={
            'enabled': True,
            'priority': 2,
            'daily_quota_tokens': 1000000,
            'daily_quota_calls': 5000,
        }
    )
    if not created:
        local.enabled = True
        local.priority = 2
        local.save(using=db_alias)
    print(f"  [OK] Local provider configured in {db_alias}")

if __name__ == "__main__":
    databases = ['default', 'default_pe', 'default_co']
    for db in databases:
        if db in settings.DATABASES:
            try:
                seed_providers_for_db(db)
            except Exception as e:
                print(f"  [X] Error seeding {db}: {e}")
        else:
            print(f"  [-] Database {db} not found in settings")
    
    print("\n--- AI Provider Synchronization Complete ---")
