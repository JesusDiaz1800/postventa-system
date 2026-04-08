import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.contrib.auth import authenticate
from apps.users.models import User
from apps.users.views import login_view
from rest_framework.test import APIRequestFactory
from unittest.mock import patch
import logging

# Configure logging to console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('apps.users.views')

factory = APIRequestFactory()
request = factory.post('/api/auth/login/', {'username': 'jdiaz', 'password': 'any'}, format='json')

try:
    u = User.objects.get(username='jdiaz')
    print(f"Testing successful login flow for user: {u.username}")
    
    with patch('apps.users.views.authenticate', return_value=u):
        response = login_view(request)
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
except User.DoesNotExist:
    print("User jdiaz does not exist in database.")
except Exception as e:
    print(f"Caught unexpected error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
