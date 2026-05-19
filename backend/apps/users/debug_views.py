from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connections
from apps.core.thread_local import get_current_country

@api_view(['GET'])
@permission_classes([AllowAny])
def test_connectivity(request):
    """
    Ultra-simple endpoint to verify API rute and tenant context.
    """
    country = get_current_country()
    db_name = connections['default'].settings_dict.get('NAME')
    
    return Response({
        "status": "online",
        "message": "Conectividad básica establecida",
        "context": {
            "detected_country": country,
            "target_db_name": db_name,
            "headers": {
                "X-Country-Code": request.headers.get('X-Country-Code')
            }
        }
    })
