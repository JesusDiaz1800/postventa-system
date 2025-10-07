"""
Monkeypatch drf-spectacular to log serializer classes being mapped during schema generation.
Run this under the project venv to capture the serializer that causes the AttributeError.
"""
import os
import sys
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
BACKEND_PKG_PATH = os.path.join(REPO_ROOT, 'backend')
if BACKEND_PKG_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PKG_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.apps.core.settings')

import django
django.setup()

import drf_spectacular.openapi as openapi
from drf_spectacular.generators import SchemaGenerator
import traceback

_orig_map_serializer = openapi.OpenApiGenerator._map_serializer

def _wrapped_map_serializer(self, serializer, direction, bypass_extensions=False):
    try:
        print(f"DEBUG: mapping serializer -> {getattr(serializer,'__name__',repr(serializer))}")
    except Exception:
        print(f"DEBUG: mapping serializer -> (repr) {repr(serializer)}")
    try:
        return _orig_map_serializer(self, serializer, direction, bypass_extensions)
    except Exception as e:
        print('\nERROR while mapping serializer:')
        traceback.print_exc()
        raise

openapi.OpenApiGenerator._map_serializer = _wrapped_map_serializer

# Run generator
try:
    gen = SchemaGenerator()
    schema = gen.get_schema(request=None, public=True)
    print('Schema generated OK')
except Exception as e:
    print('Schema generation failed:')
    traceback.print_exc()
    sys.exit(1)
