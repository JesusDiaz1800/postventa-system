#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import sys
import os

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
    try:
        from django.core.management import execute_from_command_line
        import django
        from django.conf import settings
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    
    if len(sys.argv) > 1 and 'migrate' in sys.argv:
        print(f"DEBUG: default_pe config: {settings.DATABASES.get('default_pe')}")


if __name__ == '__main__':
    main()