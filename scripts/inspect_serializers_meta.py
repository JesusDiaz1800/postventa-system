"""
Inspect installed apps' serializers modules for ModelSerializer subclasses
that are missing a Meta class or Meta.model attribute. Print findings.
"""
import os, sys
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
BACKEND_PKG_PATH = os.path.join(REPO_ROOT, 'backend')
if BACKEND_PKG_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PKG_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.apps.core.settings')
import django
django.setup()

import importlib
import inspect
from rest_framework import serializers as drf_serializers

problems = []
for app in django.apps.apps.get_app_configs():
    mod_name = f"{app.name}.serializers"
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        # skip missing serializer modules
        continue
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        try:
            if issubclass(obj, drf_serializers.ModelSerializer) and obj is not drf_serializers.ModelSerializer:
                meta = getattr(obj, 'Meta', None)
                if meta is None:
                    problems.append((mod_name, name, 'missing Meta'))
                else:
                    model = getattr(meta, 'model', None)
                    if model is None:
                        problems.append((mod_name, name, 'Meta.model missing'))
        except Exception:
            continue

if not problems:
    print('No ModelSerializer Meta problems found')
else:
    print('ModelSerializer Meta problems:')
    for mod, cls, issue in problems:
        print(f'- {mod}.{cls}: {issue}')
    sys.exit(2)
