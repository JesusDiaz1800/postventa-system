"""
Vistas para manejar adjuntos de incidencias
"""
import os
import mimetypes
from django.http import HttpResponse, FileResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

from .models import Incident, IncidentAttachment
from .serializers import IncidentAttachmentSerializer, IncidentAttachmentCreateSerializer
from apps.core.thread_local import get_current_country

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_incident_attachment(request, incident_id):
    """Subir adjunto a una incidencia"""
    try:
        # Verificar que la incidencia existe
        incident = Incident.objects.get(id=incident_id)
        
        # Verificar que se haya enviado un archivo
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No se ha enviado ningún archivo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        description = request.data.get('description', '')
        is_public = request.data.get('is_public', True)
        
        # Convertir string a boolean si es necesario
        if isinstance(is_public, str):
            is_public = is_public.lower() in ['true', '1', 'yes', 'on']
        
        # Validar tamaño del archivo (máximo 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if file.size > max_size:
            return Response(
                {'error': 'El archivo es demasiado grande. Máximo 50MB.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determinar tipo de archivo
        mime_type = file.content_type or mimetypes.guess_type(file.name)[0]
        file_type = determine_file_type(mime_type)
        
        # Crear directorio regional para adjuntos de la incidencia
        country = get_current_country()
        relative_folder = os.path.join(country, 'incident_attachments', str(incident_id))
        incident_folder = os.path.join(settings.SHARED_DOCUMENTS_PATH, relative_folder)
        os.makedirs(incident_folder, exist_ok=True)
        
        # Generar nombre único para el archivo
        file_extension = os.path.splitext(file.name)[1]
        unique_filename = f"{incident.code}_{file.name}_{request.user.id}_{file.size}{file_extension}"
        file_path_abs = os.path.join(incident_folder, unique_filename)
        file_path_rel = os.path.join(relative_folder, unique_filename)
        
        # Guardar archivo físicamente
        with open(file_path_abs, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Crear registro en la base de datos con ruta relativa regionalizada
        attachment = IncidentAttachment.objects.create(
            incident=incident,
            file_name=file.name,
            file_path=file_path_rel.replace('\\', '/'), # Guardamos ruta relativa con separador estándar
            file_size=file.size,
            file_type=file_type,
            mime_type=mime_type,
            description=description,
            uploaded_by=request.user,
            is_public=is_public
        )
        
        serializer = IncidentAttachmentSerializer(attachment)
        
        return Response({
            'success': True,
            'message': 'Archivo subido exitosamente',
            'attachment': serializer.data
        })
        
    except Incident.DoesNotExist:
        return Response(
            {'error': 'Incidencia no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error subiendo adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_incident_attachments(request, incident_id):
    """Listar adjuntos de una incidencia"""
    try:
        incident = Incident.objects.get(id=incident_id)
        attachments = IncidentAttachment.objects.filter(incident=incident)
        
        serializer = IncidentAttachmentSerializer(attachments, many=True)
        
        return Response({
            'success': True,
            'attachments': serializer.data
        })
        
    except Incident.DoesNotExist:
        return Response(
            {'error': 'Incidencia no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error listando adjuntos: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_incident_attachment(request, incident_id, attachment_id):
    """Descargar adjunto de una incidencia"""
    try:
        incident = Incident.objects.get(id=incident_id)
        attachment = IncidentAttachment.objects.get(id=attachment_id, incident=incident)
        
        # Reconstruir ruta absoluta de forma segura
        file_path_abs = os.path.normpath(os.path.join(settings.SHARED_DOCUMENTS_PATH, attachment.file_path))
        
        if not os.path.exists(file_path_abs):
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(
            open(file_path_abs, 'rb'),
            content_type=attachment.mime_type
        )
        response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
        
        return response
        
    except (Incident.DoesNotExist, IncidentAttachment.DoesNotExist):
        return Response(
            {'error': 'Recurso no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error descargando adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_incident_attachment(request, incident_id, attachment_id):
    """Ver adjunto de una incidencia en el navegador"""
    try:
        incident = Incident.objects.get(id=incident_id)
        attachment = IncidentAttachment.objects.get(id=attachment_id, incident=incident)
        
        # Reconstruir ruta absoluta de forma segura
        file_path_abs = os.path.normpath(os.path.join(settings.SHARED_DOCUMENTS_PATH, attachment.file_path))
        
        if not os.path.exists(file_path_abs):
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(
            open(file_path_abs, 'rb'),
            content_type=attachment.mime_type
        )
        response['Content-Disposition'] = f'inline; filename="{attachment.file_name}"'
        
        return response
        
    except (Incident.DoesNotExist, IncidentAttachment.DoesNotExist):
        return Response(
            {'error': 'Recurso no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error viendo adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_incident_attachment(request, incident_id, attachment_id):
    """Eliminar adjunto de una incidencia"""
    try:
        incident = Incident.objects.get(id=incident_id)
        attachment = IncidentAttachment.objects.get(id=attachment_id, incident=incident)
        
        # Verificar permisos (solo el usuario que subió el archivo o admin puede eliminarlo)
        if attachment.uploaded_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para eliminar este archivo'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Eliminar archivo físico
        file_path_abs = os.path.normpath(os.path.join(settings.SHARED_DOCUMENTS_PATH, attachment.file_path))
        if os.path.exists(file_path_abs):
            os.remove(file_path_abs)
        
        # Eliminar registro de la base de datos
        attachment.delete()
        
        return Response({
            'success': True,
            'message': 'Archivo eliminado exitosamente'
        })
        
    except (Incident.DoesNotExist, IncidentAttachment.DoesNotExist):
        return Response(
            {'error': 'Recurso no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error eliminando adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_incident_attachment_info(request, incident_id, attachment_id):
    """Obtener información de un adjunto"""
    try:
        incident = Incident.objects.get(id=incident_id)
        attachment = IncidentAttachment.objects.get(id=attachment_id, incident=incident)
        
        serializer = IncidentAttachmentSerializer(attachment)
        
        return Response({
            'success': True,
            'attachment': serializer.data
        })
        
    except (Incident.DoesNotExist, IncidentAttachment.DoesNotExist):
        return Response(
            {'error': 'Recurso no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error obteniendo información del adjunto: {e}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def determine_file_type(mime_type):
    """Determinar el tipo de archivo basado en el MIME type"""
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type in [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/csv'
        ]:
            return 'document'
    
    return 'other'
