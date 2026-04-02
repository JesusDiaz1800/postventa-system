"""
Vista optimizada para manejo de archivos adjuntos generales
Utilizado para subir respuestas de proveedores y otros documentos
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.incidents.models import Incident, IncidentImage, IncidentAttachment
from ..models import DocumentAttachment, Document
from django.db.models import Q
import logging
import os

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachment(request, incident_id=None):
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
        incident_id = incident_id or request.data.get('incident_id')
        document_type = request.data.get('document_type', 'incident_attachment')
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
        
        # 1. DocumentAttachment (Nuevos)
        attachments = DocumentAttachment.objects.filter(
            document_id=incident_id
        )
        
        # 2. Document (Legacy)
        legacy_docs = Document.objects.filter(
            incident_id=incident_id
        )

        # 3. IncidentAttachment (Incidents App)
        incident_attachments = IncidentAttachment.objects.filter(
            incident_id=incident_id
        )

        # 4. IncidentImage (Galería)
        incident_images = IncidentImage.objects.filter(
            incident_id=incident_id
        )
        
        # Filtrar por tipo si se proporciona (opcional)
        doc_type = request.query_params.get('document_type')
        if doc_type:
            attachments = attachments.filter(document_type=doc_type)
        
        # Serializar datos unificados
        data = []
        
        # Procesar DocumentAttachment
        for att in attachments:
            data.append({
                'id': f"new-{att.id}",
                'real_id': att.id,
                'model': 'DocumentAttachment',
                'filename': att.filename,
                'file_type': att.file_type,
                'file_size': att.file_size,
                'document_type': att.document_type,
                'document_type_display': att.get_document_type_display(),
                'description': att.description,
                'uploaded_by': att.uploaded_by.username if att.uploaded_by else None,
                'uploaded_at': att.uploaded_at.isoformat(),
                'file_url': att.file.url if att.file else None,
                'view_url': f"/api/documents/attachments/incident/{incident_id}/{att.id}/view/",
                'download_url': f"/api/documents/attachments/incident/{incident_id}/{att.id}/download/",
                'is_image': att.file_type.lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']
            })
            
        # Procesar Document (Legacy)
        for doc in legacy_docs:
            data.append({
                'id': f"legacy-{doc.id}",
                'real_id': doc.id,
                'model': 'Document',
                'filename': doc.filename or doc.title,
                'file_type': doc.filename.split('.')[-1] if doc.filename and '.' in doc.filename else 'pdf',
                'file_size': doc.size,
                'document_type': doc.document_type,
                'document_type_display': 'Adjunto Incidencia (Legacy)',
                'description': doc.description or doc.title,
                'uploaded_by': doc.created_by.username if doc.created_by else 'Sistema',
                'uploaded_at': doc.created_at.isoformat(),
                'file_url': doc.pdf_path or doc.file_path or None,
                'view_url': doc.pdf_path or doc.file_path or None, # Legacy docs usually have direct paths
                'download_url': doc.pdf_path or doc.file_path or None,
                'is_legacy': True,
                'is_image': (doc.filename or "").lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
            })

        # Procesar IncidentAttachment
        for iatt in incident_attachments:
            data.append({
                'id': f"incident-att-{iatt.id}",
                'real_id': iatt.id,
                'model': 'IncidentAttachment',
                'filename': iatt.file_name,
                'file_type': iatt.file_type,
                'file_size': iatt.file_size,
                'document_type': 'incident_attachment',
                'document_type_display': 'Adjunto Incidencia',
                'description': iatt.description,
                'uploaded_by': iatt.uploaded_by.username if iatt.uploaded_by else None,
                'uploaded_at': iatt.uploaded_at.isoformat(),
                'file_url': f"/api/incidents/{incident_id}/attachments/{iatt.id}/view/",
                'view_url': f"/api/incidents/{incident_id}/attachments/{iatt.id}/view/",
                'download_url': f"/api/incidents/{incident_id}/attachments/{iatt.id}/download/",
                'is_image': iatt.file_type.lower() == 'image' or iatt.file_name.lower().endswith(('.jpg', '.jpeg', '.png'))
            })

        # Procesar IncidentImage
        for img in incident_images:
            data.append({
                'id': f"image-{img.id}",
                'real_id': img.id,
                'model': 'IncidentImage',
                'filename': img.filename,
                'file_type': img.mime_type.split('/')[-1] if '/' in img.mime_type else 'image',
                'file_size': img.file_size,
                'document_type': 'incident_image',
                'document_type_display': 'Imagen de Galería',
                'description': img.caption_ai,
                'uploaded_by': img.uploaded_by.username if img.uploaded_by else None,
                'uploaded_at': img.created_at.isoformat(),
                'file_url': f"/api/incidents/{incident_id}/images/{img.id}/view/",
                'view_url': f"/api/incidents/{incident_id}/images/{img.id}/view/",
                'download_url': f"/api/incidents/{incident_id}/images/{img.id}/view/",
                'is_image': True,
                'thumbnail_url': f"/api/incidents/{incident_id}/images/{img.id}/view/"
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
