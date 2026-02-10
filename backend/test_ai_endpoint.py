import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.append(os.getcwd())
django.setup()

from apps.ai.views_writing import generate_text

def test_generate_text_view():
    User = get_user_model()
    user = User.objects.first()
    factory = RequestFactory()
    
    data = {
        "prompt": "Test prompt",
        "context": {"product": "Test pipe", "client": "Test client", "description": "Test problem"},
        "prompt_type": "quality_analysis"
    }
    
    request = factory.post('/api/ai/generate-text/', data, content_type='application/json')
    request.user = user
    
    try:
        response = generate_text(request)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
    except Exception as e:
        print(f"Error testing view: {e}")

if __name__ == '__main__':
    test_generate_text_view()
