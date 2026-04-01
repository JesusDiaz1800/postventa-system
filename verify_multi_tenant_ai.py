import os
import django
import sys

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai_orchestrator.providers import get_orchestrator
from apps.core.thread_local import set_current_country

def check_orchestrator_for(country):
    print(f"\n--- Checking AI Orchestrator for: {country} ---")
    set_current_country(country)
    
    # Re-initialize or clear cached orchestrator to force DB reload
    from apps.ai_orchestrator import providers
    providers._orchestrator = None 
    orch = providers.get_orchestrator()
    
    print(f"  Active Providers: {list(orch.providers.keys())}")
    
    if 'google' in orch.providers:
        print("  [OK] Google Provider detected")
    else:
        print("  [X] Google Provider MISSING!")
        
    if 'local' in orch.providers:
        print("  [OK] Local Provider detected")

if __name__ == "__main__":
    for country in ['CL', 'PE', 'CO']:
        check_orchestrator_for(country)
