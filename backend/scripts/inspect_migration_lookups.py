import os
import sys
from pprint import pprint

# Ensure backend package is importable
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')

import django
django.setup()

from django.forms.models import model_to_dict
from django.db.models import Count

try:
    from apps.incidents.models import Category, Responsible, Incident
except Exception as e:
    print('Error importing models:', e)
    raise

print('\n--- Categories (first 200) ---')
for c in Category.objects.all()[:200]:
    try:
        print(c.pk, model_to_dict(c))
    except Exception:
        print(c.pk, str(c))

print('\n--- Responsibles (first 200) ---')
for r in Responsible.objects.all()[:200]:
    try:
        print(r.pk, model_to_dict(r))
    except Exception:
        print(r.pk, str(r))

print('\n--- Incidents: top categoria_id counts ---')
for row in Incident.objects.values('categoria_id').annotate(count=Count('id')).order_by('-count')[:50]:
    print(row)

print('\n--- Incidents: top responsable_id counts ---')
for row in Incident.objects.values('responsable_id').annotate(count=Count('id')).order_by('-count')[:50]:
    print(row)

print('\nDone')
