from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from .models import VisitReport

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_visit_reports_simple(request):
    """
    Endpoint simple para probar visit-reports
    """
    try:
        # Intentar obtener los reportes de visita
        reports = VisitReport.objects.all()
        return Response({
            'success': True,
            'message': 'Visit reports endpoint working',
            'count': reports.count(),
            'data': []
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)
