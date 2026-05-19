"""
Vistas para análisis con IA
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import logging
from .services import AIService
from .ollama_service import OllamaService

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_image(request):
    """
    Analizar imagen real de falla en tuberías o accesorios
    """
    try:
        # Verificar que se haya enviado una imagen
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No se ha enviado ninguna imagen'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        analysis_type = request.data.get('analysis_type', 'comprehensive_technical_analysis')
        description = request.data.get('description', '')
        context = request.data.get('context', '')
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
        if image_file.content_type not in allowed_types:
            return Response(
                {'error': 'Tipo de archivo no soportado. Use JPG, PNG, GIF, WebP o BMP.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tamaño (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if image_file.size > max_size:
            return Response(
                {'error': 'El archivo es demasiado grande. Máximo 10MB.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener proveedor solicitado (opcional)
        provider_name = request.data.get('provider')
        ai_service = AIService(provider_name=provider_name)
        
        # Analizar imagen real (soporta múltiples imágenes si se envían)
        result = ai_service.analyze_real_image(
            image_files=image_file,
            analysis_type=analysis_type,
            description=description,
            context=context
        )
        
        if result['success']:
            return Response({
                'success': True,
                'analysis': result['analysis'],
                'confidence_score': result.get('confidence_score'),
                'processing_time': result.get('processing_time'),
                'tokens_used': result.get('tokens_used'),
                'model_used': result.get('model_used'),
                'analysis_id': result.get('analysis_id'),
                'message': 'Análisis de imagen completado exitosamente'
            })
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'message': 'Error al analizar la imagen'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error en analyze_image: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_failure_image(request):
    """
    Analizar imagen de falla en tuberías o accesorios (método legacy con descripción)
    """
    try:
        data = request.data
        image_description = data.get('image_description', '').strip()
        
        if not image_description:
            return Response(
                {'error': 'La descripción de la imagen es requerida'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener servicio IA
        provider_name = request.data.get('provider')
        ai_service = AIService(provider_name=provider_name)
        
        # Analizar imagen
        result = ai_service.analyze_failure_image(image_description)
        
        if result['success']:
            return Response({
                'success': True,
                'analysis': result['analysis'],
                'message': 'Análisis completado exitosamente'
            })
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'message': 'Error al analizar la imagen'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error en analyze_failure_image: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def professionalize_problem_description(request):
    """
    Redactar problema de forma profesional y justificada
    """
    try:
        data = request.data
        problem_description = data.get('problem_description', '').strip()
        
        if not problem_description:
            return Response(
                {'error': 'La descripción del problema es requerida'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener servicio IA
        provider_name = request.data.get('provider')
        ai_service = AIService(provider_name=provider_name)
        
        # Redactar problema
        result = ai_service.professionalize_problem_description(problem_description)
        
        if result['success']:
            return Response({
                'success': True,
                'redaction': result['redaction'],
                'message': 'Redacción profesional completada exitosamente'
            })
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'message': 'Error al redactar el problema'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error en professionalize_problem_description: {e}")
        
        # Manejar errores específicos de API
        error_message = str(e)
        if "API key not valid" in error_message:
            return Response(
                {'error': 'API key de Gemini no válida. Contacte al administrador.'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        elif "quota" in error_message.lower():
            return Response(
                {'error': 'Cuota de API excedida. Intente más tarde.'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        else:
            return Response(
                {'error': f'Error del servicio de IA: {error_message}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_service_status(request):
    """
    Obtener estado del servicio de IA
    """
    try:
        from django.conf import settings
        import os
        
        # Verificar si la API key está configurada
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key or api_key == 'your-gemini-api-key-here':
            return Response({
                'success': False,
                'gemini_available': False,
                'error': 'GEMINI_API_KEY no está configurada',
                'message': 'API key de Gemini no configurada. Configure GEMINI_API_KEY en el archivo .env'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Intentar inicializar el servicio principal (orquestador)
        ai_service = AIService()
        stats = ai_service._provider_instance.get_analysis_statistics() if hasattr(ai_service._provider_instance, 'get_analysis_statistics') else {}
        
        # Verificar Ollama específicamente
        ollama_status = "Not configured"
        try:
            ollama_srv = OllamaService(base_url="http://nb-jdiaz26:11434")
            # Podríamos hacer un heartbeat aquí
            ollama_status = "Available (nb-jdiaz26)"
        except:
            ollama_status = "Unavailable"

        return Response({
            'success': True,
            'gemini_available': api_key is not None,
            'ollama_available': ollama_status == "Available (nb-jdiaz26)",
            'ollama_info': ollama_status,
            'api_key_configured': api_key is not None,
            'service_status': stats,
            'current_provider': ai_service.provider_name
        })
        
    except Exception as e:
        logger.error(f"Error en get_ai_service_status: {e}")
        return Response({
            'success': False,
            'gemini_available': False,
            'error': str(e),
            'message': 'Servicio de IA no disponible'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)