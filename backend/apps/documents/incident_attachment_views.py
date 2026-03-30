"""
Vistas para gestión de adjuntos de incidencias
Permite subir, listar, descargar y eliminar archivos adjuntos de incidencias
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
from apps.incidents.models import Incident
from apps.documents.models import Document
from apps.core.thread_local import get_current_country
import logging


logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_incident_attachments(request, incident_id):
    """
    Lista todos los adjuntos de una incidencia
    """
    try:
        incident = Incident.objects.get(id=incident_id)
        
        # Obtener adjuntos de la incidencia
        attachments = Document.objects.filter(
            incident_id=incident_id,
            document_type='incident_attachment'
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
            'incident_id': incident_id,
            'incident_code': incident.code,
            'attachments': attachments_data,
            'total': len(attachments_data)
        })
        
    except Incident.DoesNotExist:
        return Response(
            {'error': 'Incidencia no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error listing incident attachments: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_incident_attachment(request, incident_id):
    """
    Sube un archivo adjunto a una incidencia
    """
    try:
        incident = Incident.objects.get(id=incident_id)
        
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
        country = get_current_country()
        incident_dir = os.path.join(settings.SHARED_DOCUMENTS_PATH, country, 'incident_attachments', f'incident_{incident_id}')
        os.makedirs(incident_dir, exist_ok=True)

        
        # Guardar archivo
        file_path = os.path.join(incident_dir, file.name)
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Crear registro en base de datos
        document = Document.objects.create(
            incident=incident,
            title=title,
            filename=file.name,
            description=description,
            document_type='incident_attachment',
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
        
    except Incident.DoesNotExist:
        return Response(
            {'error': 'Incidencia no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error uploading incident attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_incident_attachment(request, incident_id, attachment_id):
    """
    Descarga un archivo adjunto de una incidencia
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=incident_id,
            document_type='incident_attachment'
        )
        
        if not os.path.exists(document.file_path):
            # Fallback regional: Reconstruir ruta con país actual si el guardado en DB no fue absoluto/regionalizado
            country = get_current_country()
            filename = os.path.basename(document.file_path)
            fallback_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, country, 'incident_attachments', f'incident_{incident_id}', filename)
            
            if os.path.exists(fallback_path):
                document.file_path = fallback_path
            else:
                # Segundo fallback: Ruta legacy (sin país)
                legacy_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, 'incident_attachments', f'incident_{incident_id}', filename)
                if os.path.exists(legacy_path):
                    document.file_path = legacy_path
                else:
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
        logger.error(f"Error downloading incident attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_incident_attachment(request, incident_id, attachment_id):
    """
    Visualiza un archivo adjunto de una incidencia en el navegador
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=incident_id,
            document_type='incident_attachment'
        )
        
        if not os.path.exists(document.file_path):
            # Fallback regional
            country = get_current_country()
            filename = os.path.basename(document.file_path)
            fallback_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, country, 'incident_attachments', f'incident_{incident_id}', filename)
            
            if os.path.exists(fallback_path):
                document.file_path = fallback_path
            else:
                # Segundo fallback: Ruta legacy
                legacy_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, 'incident_attachments', f'incident_{incident_id}', filename)
                if os.path.exists(legacy_path):
                    document.file_path = legacy_path
                else:
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
        logger.error(f"Error viewing incident attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_incident_attachment(request, incident_id, attachment_id):
    """
    Elimina un archivo adjunto de una incidencia
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=incident_id,
            document_type='incident_attachment'
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
        logger.error(f"Error deleting incident attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_incident_attachment_info(request, incident_id, attachment_id):
    """
    Obtiene información detallada de un adjunto de incidencia
    """
    try:
        document = Document.objects.get(
            id=attachment_id,
            incident_id=incident_id,
            document_type='incident_attachment'
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
        logger.error(f"Error getting incident attachment info: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
