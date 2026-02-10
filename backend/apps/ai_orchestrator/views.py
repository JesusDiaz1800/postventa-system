from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone

from .models import AIProvider, AIAnalysis
from .providers import get_orchestrator
from .serializers import AIProviderSerializer, AIAnalysisSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_image(request):
    """Analyze an image using AI providers"""
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No se proporcionó imagen'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return Response(
            {'error': 'Tipo de archivo no permitido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Read image data
    image_data = image_file.read()
    
    # Analyze using orchestrator
    orchestrator = get_orchestrator()
    result = orchestrator.analyze_image(image_data, image_file.content_type)
    
    if result.get('success'):
        # Log the analysis
        AIAnalysis.objects.create(
            analysis_type='image_analysis',
            input_data={
                'filename': image_file.name,
                'size': image_file.size,
                'type': image_file.content_type
            },
            output_data=result['data'],
            confidence_score=0.8,  # Default confidence
            tokens_used=result.get('tokens_used', 0),
            processing_time=result.get('processing_time', 0)
        )
        
        return Response({
            'success': True,
            'data': result['data'],
            'provider_used': result.get('provider'),
            'tokens_used': result.get('tokens_used', 0),
            'processing_time': result.get('processing_time', 0)
        })
    
    else:
        error_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if result.get('code') == 429:
            error_code = status.HTTP_429_TOO_MANY_REQUESTS
            
        return Response(
            {
                'error': result.get('error', 'Error en el análisis'),
                'next_reset': result.get('next_reset')
            }, 
            status=error_code
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_text(request):
    """Generate text using AI providers"""
    prompt = request.data.get('prompt')
    context = request.data.get('context', {})
    analysis_type = request.data.get('analysis_type', 'text_rewrite')
    
    if not prompt:
        return Response(
            {'error': 'Prompt es requerido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate text using orchestrator
    orchestrator = get_orchestrator()
    result = orchestrator.generate_text(prompt, context)
    
    if result.get('success'):
        # Log the analysis
        AIAnalysis.objects.create(
            analysis_type=analysis_type,
            input_data={'prompt': prompt, 'context': context},
            output_data={'text': result['text']},
            tokens_used=result.get('tokens_used', 0),
            processing_time=result.get('processing_time', 0)
        )
        
        return Response({
            'success': True,
            'text': result['text'],
            'provider_used': result.get('provider'),
            'tokens_used': result.get('tokens_used', 0),
            'processing_time': result.get('processing_time', 0)
        })
    
    else:
        error_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if result.get('code') == 429:
            error_code = status.HTTP_429_TOO_MANY_REQUESTS
            
        return Response(
            {
                'error': result.get('error', 'Error en la generación de texto'),
                'next_reset': result.get('next_reset')
            }, 
            status=error_code
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def provider_status(request):
    """Get status of all AI providers"""
    # Datos mock temporal hasta que el orchestrator esté configurado
    status_list = [
        {
            'id': 'openai-gpt4',
            'name': 'OpenAI GPT-4',
            'type': 'text_generation',
            'enabled': True,
            'status': 'active',
            'quota_used': 1250,
            'quota_limit': 10000,
            'last_used': '2025-09-10T14:30:00Z',
            'response_time': 1.2,
            'success_rate': 98.5
        },
        {
            'id': 'openai-dalle',
            'name': 'OpenAI DALL-E',
            'type': 'image_generation',
            'enabled': True,
            'status': 'active',
            'quota_used': 45,
            'quota_limit': 500,
            'last_used': '2025-09-10T12:15:00Z',
            'response_time': 3.8,
            'success_rate': 95.2
        },
        {
            'id': 'anthropic-claude',
            'name': 'Anthropic Claude',
            'type': 'text_generation',
            'enabled': False,
            'status': 'inactive',
            'quota_used': 0,
            'quota_limit': 5000,
            'last_used': None,
            'response_time': 0,
            'success_rate': 0
        }
    ]
    
    # Usar el orquestador real si está disponible
    try:
        orchestrator = get_orchestrator()
        actual_status = orchestrator.get_provider_status()
        if actual_status:
            return Response({
                'providers': actual_status,
                'timestamp': timezone.now().isoformat()
            })
    except Exception:
        pass
        
    return Response({
        'providers': status_list,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analysis_history(request):
    """Get AI analysis history"""
    analyses = AIAnalysis.objects.all().order_by('-created_at')[:50]
    serializer = AIAnalysisSerializer(analyses, many=True)
    
    return Response({
        'analyses': serializer.data,
        'count': analyses.count()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reset_quotas(request):
    """Reset quotas for all providers (admin only)"""
    if not request.user.is_admin():
        return Response(
            {'error': 'Solo los administradores pueden resetear cuotas'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    from .tasks import reset_quotas_task
    task = reset_quotas_task.delay()
    
    return Response({
        'message': 'Reset de cuotas iniciado',
        'task_id': task.id
    }, status=status.HTTP_202_ACCEPTED)
