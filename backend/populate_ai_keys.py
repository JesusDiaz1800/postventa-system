import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai_orchestrator.models import AIProvider
from django.utils import timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_keys():
    print(f"--- Populating AI Keys from Environment ({timezone.now()}) ---")
    
    # Map provider names to settings variables
    key_mapping = {
        'google': 'GEMINI_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY'
    }
    
    for provider_name, env_var in key_mapping.items():
        try:
            api_key = getattr(settings, env_var, None)
            
            # Also try os.environ as fallback
            if not api_key:
                api_key = os.environ.get(env_var)
                
            if not api_key:
                print(f"WARNING: No API Key found for {provider_name} (checked settings.{env_var} and os.environ)")
                continue
                
            # Get or create provider
            provider, created = AIProvider.objects.get_or_create(
                name=provider_name,
                defaults={'enabled': True}
            )
            
            # Set key (this handles encryption)
            provider.set_api_key(api_key)
            provider.enabled = True
            provider.save()
            
            print(f"SUCCESS: Updated API Key for {provider_name} (Created: {created})")
            
        except Exception as e:
            print(f"ERROR updating {provider_name}: {str(e)}")

    print("-" * 30)
    print("Verification:")
    for p in AIProvider.objects.filter(enabled=True):
        has_key = bool(p.get_api_key())
        print(f"  {p.name}: Key Set = {has_key}, Enabled = {p.enabled}")

if __name__ == '__main__':
    populate_keys()
