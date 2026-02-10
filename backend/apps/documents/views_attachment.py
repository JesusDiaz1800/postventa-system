"""
Vista optimizada para manejo de archivos adjuntos generales
Utilizado para subir respuestas de proveedores y otros documentos
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.incidents.models import Incident
from .models import DocumentAttachment
from django.db.models import Q
import logging
import os

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachment(request):
    """
    Endpoint optimizado para subir archivos adjuntos
    
    Parámetros esperados:
    - file: Archivo a subir (requerido)
    - incident_id: ID de la incidencia (requerido)
    - document_type: Tipo de documento (requerido: supplier_response, visit_report, lab_report, etc.)
    - description: Descripción del archivo (opcional)
    
    Retorna:
    - 201: Archivo subido exitosamente
    - 400: Datos inválidos
    - 404: Incidencia no encontrada
    """
    try:
        # 1. Validar datos requeridos
        file = request.FILES.get('file')
        incident_id = request.data.get('incident_id')
        document_type = request.data.get('document_type')
        description = request.data.get('description', '')
        
        if not file:
            return Response(
                {'error': 'No se proporcionó ningún archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not incident_id:
            return Response(
                {'error': 'El incident_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not document_type:
            return Response(
                {'error': 'El document_type es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Validar que la incidencia existe
        incident = get_object_or_404(Incident, pk=incident_id)
        
        # 3. Validar tipo de documento
        valid_types = [choice[0] for choice in DocumentAttachment.DOCUMENT_TYPES]
        if document_type not in valid_types:
            return Response(
                {'error': f'Tipo de documento inválido. Tipos permitidos: {", ".join(valid_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 4. Extraer información del archivo
        filename = file.name
        file_size = file.size
        file_extension = os.path.splitext(filename)[1].lower()
        
        # 5. Validar extensiones permitidas
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.txt']
        if file_extension not in allowed_extensions:
            return Response(
                {'error': f'Extensión de archivo no permitida. Extensiones permitidas: {", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 6. Crear el DocumentAttachment
        attachment = DocumentAttachment.objects.create(
            document_type=document_type,
            document_id=incident_id,  # En este caso, document_id almacena el incident_id
            file=file,
            filename=filename,
            file_type=file_extension[1:],  # Remover el punto
            file_size=file_size,
            description=description,
            uploaded_by=request.user
        )
        
        logger.info(f"Archivo adjunto creado exitosamente: {attachment.id} - {filename} para incidencia {incident_id}")
        
        # 7. Retornar respuesta exitosa
        return Response({
            'success': True,
            'message': 'Archivo subido exitosamente',
            'attachment_id': attachment.id,
            'filename': attachment.filename,
            'file_type': attachment.file_type,
            'file_size': attachment.file_size,
            'document_type': attachment.get_document_type_display(),
            'uploaded_at': attachment.uploaded_at.isoformat(),
            'uploaded_by': request.user.username
        }, status=status.HTTP_201_CREATED)
        
    except Incident.DoesNotExist:
        return Response(
            {'error': f'Incidencia con ID {incident_id} no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error al subir archivo adjunto: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno al subir el archivo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_attachments_by_incident(request, incident_id):
    """
    Lista todos los archivos adjuntos de una incidencia
    
    Parámetros:
    - incident_id: ID de la incidencia
    - document_type (query param, opcional): Filtrar por tipo de documento
    """
    try:
        # Validar que la incidencia existe
        incident = get_object_or_404(Incident, pk=incident_id)
        
        # Obtener attachments
        # Obtener attachments directos de la incidencia
        attachments = DocumentAttachment.objects.filter(
            document_id=incident_id
        )
        
        # Filtrar por tipo si se proporciona
        doc_type = request.query_params.get('document_type')
        if doc_type:
            attachments = attachments.filter(document_type=doc_type)
        
        # Serializar datos
        data = []
        for attachment in attachments:
            data.append({
                'id': attachment.id,
                'filename': attachment.filename,
                'file_type': attachment.file_type,
                'file_size': attachment.file_size,
                'document_type': attachment.document_type,
                'document_type_display': attachment.get_document_type_display(),
                'description': attachment.description,
                'uploaded_by': attachment.uploaded_by.username if attachment.uploaded_by else None,
                'uploaded_at': attachment.uploaded_at.isoformat(),
                'file_url': attachment.file.url if attachment.file else None
            })
        
        return Response({
            'success': True,
            'count': len(data),
            'attachments': data
        })
        
    except Incident.DoesNotExist:
        return Response(
            {'error': f'Incidencia con ID {incident_id} no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error al listar archivos adjuntos: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_attachment(request, incident_id, attachment_id):
    """
    Descarga un archivo adjunto específico
    """
    try:
        from django.http import FileResponse
        
        # Validar que el attachment existe y pertenece a la incidencia
        attachment = get_object_or_404(
            DocumentAttachment, 
            id=attachment_id, 
            document_id=incident_id
        )
        
        # Verificar que el archivo existe
        if not attachment.file:
            return Response(
                {'error': 'El archivo no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Retornar el archivo
        response = FileResponse(attachment.file.open('rb'), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        return response
        
    except DocumentAttachment.DoesNotExist:
        return Response(
            {'error': 'Archivo adjunto no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error al descargar archivo adjunto: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error al descargar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_attachment(request, incident_id, attachment_id):
    """
    Visualiza un archivo adjunto en el navegador
    """
    try:
        from django.http import FileResponse
        import mimetypes
        
        # Validar que el attachment existe y pertenece a la incidencia
        attachment = get_object_or_404(
            DocumentAttachment, 
            id=attachment_id, 
            document_id=incident_id
        )
        
        # Verificar que el archivo existe
        if not attachment.file:
            return Response(
                {'error': 'El archivo no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determinar el content type
        content_type, _ = mimetypes.guess_type(attachment.filename)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Retornar el archivo para visualización
        response = FileResponse(attachment.file.open('rb'), content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{attachment.filename}"'
        return response
        
    except DocumentAttachment.DoesNotExist:
        return Response(
            {'error': 'Archivo adjunto no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error al visualizar archivo adjunto: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error al visualizar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_attachment(request, incident_id, attachment_id):
    """
    Elimina un archivo adjunto
    """
    try:
        # Validar que el attachment existe y pertenece a la incidencia
        attachment = get_object_or_404(
            DocumentAttachment, 
            id=attachment_id, 
            document_id=incident_id
        )
        
        # Guardar info antes de eliminar
        filename = attachment.filename
        
        # Eliminar el archivo físico y el registro
        if attachment.file:
            attachment.file.delete()
        attachment.delete()
        
        logger.info(f"Archivo adjunto eliminado: {attachment_id} - {filename}")
        
        return Response({
            'success': True,
            'message': f'Archivo "{filename}" eliminado exitosamente'
        }, status=status.HTTP_200_OK)
        
    except DocumentAttachment.DoesNotExist:
        return Response(
            {'error': 'Archivo adjunto no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error al eliminar archivo adjunto: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error al eliminar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
