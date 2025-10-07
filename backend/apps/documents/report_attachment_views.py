"""
Vistas para gestión de adjuntos de reportes
Permite subir, listar, descargar y eliminar archivos adjuntos de reportes
"""
import os
import json
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.documents.models import Document
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_report_attachments(request, report_id, report_type):
    """
    Lista todos los adjuntos de un reporte
    """
    try:
        # Obtener adjuntos del reporte
        attachments = Document.objects.filter(
            incident_id=report_id,  # Usar report_id como incident_id para la lógica existente
            document_type=report_type
        ).order_by('-created_at')
        
        attachments_data = []
        for attachment in attachments:
            attachments_data.append({
                'id': attachment.id,
                'filename': attachment.filename,
                'title': attachment.title,
                'description': attachment.description,
                'size': attachment.size,
                'created_at': attachment.created_at,
                'created_by': attachment.created_by.username if attachment.created_by else 'Sistema',
                'is_public': getattr(attachment, 'is_public', False),
                'document_type': attachment.document_type,
            })
        
        return Response({
            'report_id': report_id,
            'report_type': report_type,
            'attachments': attachments_data,
            'total': len(attachments_data)
        })
        
    except Exception as e:
        logger.error(f"Error listing report attachments: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_report_attachment(request, report_id, report_type):
    """
    Sube un archivo adjunto a un reporte
    """
    try:
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No se proporcionó ningún archivo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        title = request.data.get('title', file.name)
        description = request.data.get('description', '')
        is_public = request.data.get('is_public', 'false').lower() == 'true'
        
        # Crear directorio si no existe
        report_dir = os.path.join(settings.SHARED_DOCUMENTS_PATH, f'{report_type}s', f'report_{report_id}')
        os.makedirs(report_dir, exist_ok=True)
        
        # Guardar archivo
        file_path = os.path.join(report_dir, file.name)
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Crear registro en base de datos
        document = Document.objects.create(
            incident_id=report_id,  # Usar report_id como incident_id
            title=title,
            filename=file.name,
            description=description,
            document_type=report_type,
            file_path=file_path,
            size=file.size,
            created_by=request.user,
            is_public=is_public
        )
        
        return Response({
            'id': document.id,
            'filename': document.filename,
            'title': document.title,
            'description': document.description,
            'size': document.size,
            'created_at': document.created_at,
            'is_public': document.is_public,
            'message': 'Archivo adjunto subido exitosamente'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error uploading report attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report_attachment(request, report_id, report_type, attachment_id):
    """
    Descarga un archivo adjunto de un reporte
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=report_id,
            document_type=report_type
        )
        
        if not os.path.exists(document.file_path):
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(
            open(document.file_path, 'rb'),
            as_attachment=True,
            filename=document.filename
        )
        return response
        
    except Document.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error downloading report attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_report_attachment(request, report_id, report_type, attachment_id):
    """
    Visualiza un archivo adjunto de un reporte en el navegador
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=report_id,
            document_type=report_type
        )
        
        if not os.path.exists(document.file_path):
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determinar el tipo de contenido
        content_type = 'application/octet-stream'
        if document.filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif document.filename.lower().endswith(('.jpg', '.jpeg')):
            content_type = 'image/jpeg'
        elif document.filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif document.filename.lower().endswith(('.doc', '.docx')):
            content_type = 'application/msword'
        elif document.filename.lower().endswith(('.xls', '.xlsx')):
            content_type = 'application/vnd.ms-excel'
        
        response = FileResponse(
            open(document.file_path, 'rb'),
            content_type=content_type,
            filename=document.filename
        )
        return response
        
    except Document.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error viewing report attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_report_attachment(request, report_id, report_type, attachment_id):
    """
    Elimina un archivo adjunto de un reporte
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=report_id,
            document_type=report_type
        )
        
        # Eliminar archivo físico si existe
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Eliminar registro de base de datos
        document.delete()
        
        return Response({
            'message': 'Adjunto eliminado exitosamente'
        })
        
    except Document.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting report attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_attachment_info(request, report_id, report_type, attachment_id):
    """
    Obtiene información detallada de un adjunto de reporte
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=report_id,
            document_type=report_type
        )
        
        return Response({
            'id': document.id,
            'filename': document.filename,
            'title': document.title,
            'description': document.description,
            'size': document.size,
            'created_at': document.created_at,
            'created_by': document.created_by.username if document.created_by else 'Sistema',
            'is_public': getattr(document, 'is_public', False),
            'document_type': document.document_type,
            'file_exists': os.path.exists(document.file_path) if document.file_path else False
        })
        
    except Document.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting report attachment info: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

