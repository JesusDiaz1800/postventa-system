import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.ai_orchestrator.models import AIProvider
from django.utils import timezone

print(f"--- AI Provider Status Check ({timezone.now()}) ---")
providers = AIProvider.objects.all().order_by('priority')

if not providers.exists():
    print("WARNING: No AI Providers found in database!")
else:
    for p in providers:
        print(f"Provider: {p.name}")
        print(f"  Enabled: {p.enabled}")
        print(f"  Priority: {p.priority}")
        print(f"  API Key Set: {'YES' if p.get_api_key() else 'NO'}")
        print(f"  Next Reset: {p.get_next_reset_time()}")
        print(f"  Calls Today: {p.calls_made_today} / {p.daily_quota_calls}")
        print(f"  Tokens Today: {p.tokens_used_today} / {p.daily_quota_tokens}")
        print(f"  Has Quota: {p.has_quota()}")
        print("-" * 30)
