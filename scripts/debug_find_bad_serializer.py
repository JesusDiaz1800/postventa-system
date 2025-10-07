"""
Diagnostics: find serializer classes that fail to build fields (used to debug drf-spectacular schema error).
Run this with the project PYTHONPATH and DJANGO_SETTINGS_MODULE set. It will import every `serializers.py` in installed apps
and try to instantiate serializer classes and access `.fields` to trigger model introspection errors.
"""
import os
import sys
import importlib
import pkgutil

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
os.chdir(REPO_ROOT)
# Ensure repo root is on sys.path so `backend` package can be imported
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
# Also ensure the backend package path is on sys.path so imports like `apps.foo` work
BACKEND_PKG_PATH = os.path.join(REPO_ROOT, 'backend')
if BACKEND_PKG_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PKG_PATH)
# Set DJANGO_SETTINGS_MODULE if not already set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.apps.core.settings')

import django
django.setup()

from importlib import import_module
from inspect import isclass

from rest_framework import serializers as drf_serializers

errors = []

# Iterate installed apps and try to import their serializers module if present
for app_config in django.apps.apps.get_app_configs():
    mod_name = f"{app_config.name}.serializers"
    try:
        mod = import_module(mod_name)
    except Exception as e:
        # ignore import errors here (they might be expected), but record them
        errors.append((mod_name, f"import error: {e}"))
        continue
    # inspect attributes
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        try:
            if isclass(attr) and issubclass(attr, drf_serializers.BaseSerializer):
                # Try to instantiate with no data/context if possible
                try:
                    inst = attr()
                except Exception:
                    # try with context fallback
                    try:
                        inst = attr(context={})
                    except Exception as e:
                        errors.append((mod_name + "." + attr_name, f"instantiation error: {e}"))
                        continue
                # Access fields to force model introspection
                try:
                    _ = getattr(inst, 'fields', None)
                except Exception as e:
                    errors.append((mod_name + "." + attr_name, f"fields error: {e}"))
        except Exception:
            pass

# Print results
if not errors:
    print('No failures detected when instantiating serializers.')
else:
    print('Problems detected:')
    for loc, msg in errors:
        print(f"- {loc}: {msg}")

# Exit non-zero if errors found
if errors:
    sys.exit(2)
