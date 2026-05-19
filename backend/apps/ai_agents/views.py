"""
API Views for AI Agents

Exposes the PostventaAgent functionality via REST endpoints.
"""

import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .agent import get_agent

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_query(request):
    """
    Send a query to the AI Agent
    
    POST /api/ai-agents/query/
    {
        "query": "¿Cuáles son los pasos para una soldadura por polifusión?",
        "context": {"incident_id": 123}  // optional
    }
    
    Returns:
    {
        "success": true,
        "response": "Los pasos para una soldadura...",
        "confidence": 0.85,
        "sources": ["Manual de Instalación"],
        "reasoning": "Query is a direct question | Found 2 relevant documents"
    }
    """
    try:
        data = request.data
        query = data.get('query', '').strip()
        
        if not query:
            return Response(
                {'error': 'La consulta es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        context = data.get('context', {})
        
        # Add user info to context
        context['user_id'] = request.user.id
        context['username'] = request.user.username
        
        # Get agent and run query
        agent = get_agent()
        result = agent.run(query=query, context=context)
        
        if result.get('error'):
            logger.warning(f"Agent query warning: {result['error']}")
        
        return Response({
            'success': True,
            'response': result['response'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'reasoning': result['reasoning'],
            'iterations': result['iterations'],
            'analysis_data': result.get('analysis_data'),
            'engine_provider': result.get('engine_provider', 'unknown'),
        })
        
    except Exception as e:
        logger.error(f"Agent query error: {e}")
        return Response(
            {'error': f'Error del agente: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def agent_analyze_image(request):
    """
    Analyze images using the AI Agent
    
    POST /api/ai-agents/analyze-image/
    FormData:
        - images: File (multiple allowed)
        - image: File (legacy support)
        - query: String (optional question about the image)
    """
    try:
        # Extreme Debug logging
        logger.info("--- DEBUG AI AGENTS: START ---")
        logger.info(f"User: {request.user}")
        logger.info(f"Content-Type received: {request.content_type}")
        logger.info(f"FILES keys present: {list(request.FILES.keys())}")
        logger.info(f"DATA keys present: {list(request.data.keys())}")
        
        # Log filenames if present
        for key in request.FILES:
            files_list = request.FILES.getlist(key)
            logger.info(f"  Field '{key}': {[f.name for f in files_list]}")

        # Support multiple keys for flexibility
        images = []
        for key in ['images', 'image', 'file', 'files']:
            found = request.FILES.getlist(key)
            if found:
                images.extend(found)
                logger.info(f"Found {len(found)} image(s) in field '{key}'")

        if not images:
            logger.error(f"Validation failed: No images found. Context: CT={request.content_type}, FILES={list(request.FILES.keys())}")
            return Response(
                {
                    'error': 'No se ha enviado ninguna imagen',
                    'debug': {
                        'content_type': request.content_type,
                        'files_found': list(request.FILES.keys()),
                        'data_found': list(request.data.keys()),
                        'hint': 'Asegúrese de usar FormData y adjuntar archivos en los campos: images, image o file.'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Proceeding to analyze {len(images)} images.")
        
        query = request.data.get('query', 'Analiza estas imágenes de manera técnica')
        
        # Read image bytes for all images
        image_bytes_list = []
        for image_file in images:
            image_file.seek(0)
            image_bytes_list.append(image_file.read())
        
        # Get agent and run with images
        agent = get_agent()
        result = agent.run(query=query, images=image_bytes_list)
        
        return Response({
            'success': True,
            'response': result['response'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'],
            'analysis_data': result.get('analysis_data')
        })
        
    except Exception as e:
        logger.error(f"Agent image analysis error: {e}")
        return Response(
            {'error': f'Error al analizar imagen: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_generate_report(request):
    """
    Generate professional technical report from analysis
    
    POST /api/ai-agents/generate-report/
    Body:
        - analysis_data: Dict (from previous analysis)
        - chat_history: List (optional context)
    """
    try:
        analysis_data = request.data.get('analysis_data', {})
        chat_history = request.data.get('chat_history', [])
        
        if not analysis_data and not chat_history:
            return Response(
                {'error': 'No se han proporcionado datos para el reporte'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        from apps.ai.gemini_service import get_gemini_service
        service = get_gemini_service()
        
        # Call the service method we just added
        result = service.generate_technical_report(analysis_data, chat_history)
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(
                {'error': result.get('error', 'Error generando reporte')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Agent report generation error: {e}")
        return Response(
            {'error': f'Error generando reporte: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_status(request):
    """
    Get the status of the AI Agent system
    
    GET /api/ai-agents/status/
    """
    try:
        agent = get_agent()
        
        # Check provider availability
        provider_available = agent.provider_manager is not None
        
        # Check Knowledge Base availability
        kb_available = False
        try:
            from apps.ai.vector_store import get_vector_store
            store = get_vector_store()
            kb_available = store.count() > 0
        except:
            pass
        
        return Response({
            'success': True,
            'agent_ready': True,
            'provider_available': provider_available,
            'knowledge_base_available': kb_available,
            'knowledge_engine': 'VectorStoreLite (Numpy)',
            'max_iterations': agent.max_iterations,
        })
        
    except Exception as e:
        logger.error(f"Agent status error: {e}")
        return Response({
            'success': False,
            'agent_ready': False,
            'error': str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
