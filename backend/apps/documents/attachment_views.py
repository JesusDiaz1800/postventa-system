"""
Vistas para gestión de archivos adjuntos de documentos
"""
import os
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .attachment_service import attachment_service
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachment(request, document_type, document_id):
    """Subir archivo adjunto a un documento"""
    try:
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No se proporcionó archivo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        description = request.data.get('description', '')
        
        # Validar tipo de documento
        valid_types = ['visit_report', 'lab_report', 'supplier_report']
        if document_type not in valid_types:
            return Response(
                {'error': f'Tipo de documento inválido. Tipos válidos: {valid_types}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tamaño del archivo (máx. 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            return Response(
                {'error': 'El archivo es demasiado grande. Máximo 10MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar archivo
        file_info = attachment_service.save_attachment(
            file, document_type, document_id, description
        )
        
        return Response({
            'message': 'Archivo subido exitosamente',
            'file_info': file_info
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error subiendo archivo adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_attachments(request, document_type, document_id):
    """Listar archivos adjuntos de un documento"""
    try:
        attachments = attachment_service.list_attachments(document_type, document_id)
        
        return Response({
            'attachments': attachments,
            'count': len(attachments)
        })
        
    except Exception as e:
        logger.error(f"Error listando archivos adjuntos: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_attachment(request, document_type, document_id, filename):
    """Descargar archivo adjunto"""
    try:
        file_path = attachment_service.get_attachment_path(document_type, document_id, filename)
        
        if not os.path.exists(file_path):
            raise Http404("Archivo no encontrado")
        
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error descargando archivo adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_attachment(request, document_type, document_id, filename):
    """Ver archivo adjunto en el navegador"""
    try:
        file_path = attachment_service.get_attachment_path(document_type, document_id, filename)
        
        if not os.path.exists(file_path):
            raise Http404("Archivo no encontrado")
        
        # Determinar tipo de contenido
        content_type = 'application/octet-stream'
        if filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            content_type = 'image/jpeg'
        elif filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif filename.lower().endswith('.gif'):
            content_type = 'image/gif'
        elif filename.lower().endswith('.txt'):
            content_type = 'text/plain'
        elif filename.lower().endswith('.html'):
            content_type = 'text/html'
        
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
            
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error viendo archivo adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_attachment(request, document_type, document_id, filename):
    """Eliminar archivo adjunto"""
    try:
        success = attachment_service.delete_attachment(document_type, document_id, filename)
        
        if success:
            return Response({
                'message': 'Archivo eliminado exitosamente'
            })
        else:
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Error eliminando archivo adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attachment_info(request, document_type, document_id, filename):
    """Obtener información de un archivo adjunto"""
    try:
        file_info = attachment_service.get_attachment_info(document_type, document_id, filename)
        
        if file_info:
            return Response(file_info)
        else:
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Error obteniendo información de archivo adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
