import sys
import os

# Agregar site-packages al path
python_home = os.path.dirname(__file__)
site_packages = os.path.join(python_home, 'Lib', 'site-packages')

if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

