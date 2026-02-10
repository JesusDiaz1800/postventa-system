
import sys
import os

print(f"CWD: {os.getcwd()}")
print("SYS.PATH:")
for p in sys.path:
    print(f"  - {p}")

try:
    import apps
    print(f"SUCCESS: Imported apps from {apps.__file__}")
except ImportError as e:
    print(f"ERROR: Could not import apps: {e}")

try:
    from apps.core import settings
    print("SUCCESS: Imported settings")
except ImportError as e:
    print(f"ERROR: Could not import settings: {e}")
