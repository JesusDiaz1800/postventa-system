"""
Vistas para gestión de adjuntos específicos de reportes de proveedores
Maneja dos tipos de documentos: "reporte_para_proveedor" y "respuesta_de_proveedor"
"""

import os
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import SupplierReport, DocumentAttachment
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)

def get_supplier_report_attachments_path(report_id, document_type):
    """Obtiene la ruta para los adjuntos de reportes de proveedores"""
    base_path = Path(settings.SHARED_DOCUMENTS_PATH)
    supplier_path = base_path / "supplier_reports" / str(report_id) / document_type
    supplier_path.mkdir(parents=True, exist_ok=True)
    return supplier_path

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_supplier_report_attachments(request, report_id):
    """Lista todos los adjuntos de un reporte de proveedor"""
    try:
        # Verificar que el reporte existe
        report = SupplierReport.objects.get(id=report_id)
        
        # Obtener adjuntos de la base de datos
        attachments = DocumentAttachment.objects.filter(
            document_type='supplier_report',
            document_id=report_id
        ).order_by('-uploaded_at')
        
        # Formatear respuesta
        attachments_data = []
        for attachment in attachments:
            attachment_data = {
                'id': attachment.id,
                'filename': attachment.filename,
                'title': attachment.filename,
                'description': attachment.description,
                'document_type': getattr(attachment, 'supplier_document_type', 'unknown'),
                'size': attachment.file_size,
                'created_at': attachment.uploaded_at,
                'created_by': attachment.uploaded_by.username if attachment.uploaded_by else 'Sistema',
                'is_public': True,  # Por defecto público
                'file_path': attachment.file.path if attachment.file else None,
            }
            attachments_data.append(attachment_data)
        
        return Response({
            'success': True,
            'attachments': attachments_data,
            'report_id': report_id,
            'report_title': report.title
        })
        
    except SupplierReport.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Reporte de proveedor no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error listing supplier report attachments: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_supplier_report_attachment(request, report_id):
    """Sube un adjunto para un reporte de proveedor"""
    try:
        # Verificar que el reporte existe
        report = SupplierReport.objects.get(id=report_id)
        
        # Validar datos
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No se proporcionó archivo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        document_type = request.data.get('document_type', 'reporte_para_proveedor')
        description = request.data.get('description', '')
        is_public = request.data.get('is_public', 'false').lower() == 'true'
        
        # Validar tipo de documento
        valid_types = ['reporte_para_proveedor', 'respuesta_de_proveedor']
        if document_type not in valid_types:
            return Response({
                'success': False,
                'error': f'Tipo de documento inválido. Debe ser uno de: {", ".join(valid_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear directorio si no existe
        attachments_path = get_supplier_report_attachments_path(report_id, document_type)
        
        # Generar nombre único para el archivo
        file_extension = os.path.splitext(file.name)[1]
        unique_filename = f"{document_type}_{report_id}_{file.name}"
        
        # Guardar archivo usando el FileField del modelo
        attachment = DocumentAttachment.objects.create(
            document_type='supplier_report',
            document_id=report_id,
            filename=unique_filename,
            file_type=file.content_type,
            file_size=file.size,
            description=description,
            uploaded_by=request.user,
            file=file  # Django manejará la subida automáticamente
        )
        
        # Agregar el tipo de documento de proveedor como atributo personalizado
        attachment.supplier_document_type = document_type
        attachment.save()
        
        return Response({
            'success': True,
            'message': 'Archivo adjuntado exitosamente',
            'attachment': {
                'id': attachment.id,
                'filename': attachment.filename,
                'title': attachment.filename,
                'description': attachment.description,
                'document_type': document_type,
                'size': attachment.file_size,
                'created_at': attachment.uploaded_at,
                'created_by': attachment.uploaded_by.username,
                'is_public': True
            }
        })
        
    except SupplierReport.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Reporte de proveedor no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error uploading supplier report attachment: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_supplier_report_attachment(request, attachment_id):
    """Descarga un adjunto de reporte de proveedor"""
    try:
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_type='supplier_report'
        )
        
        # Verificar permisos (por ahora todos los archivos son públicos)
        # if attachment.uploaded_by != request.user:
        #     return Response({
        #         'success': False,
        #         'error': 'No tienes permisos para acceder a este archivo'
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que el archivo existe
        if not attachment.file or not attachment.file.name:
            return Response({
                'success': False,
                'error': 'Archivo no encontrado en el servidor'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Leer archivo
        try:
            with attachment.file.open('rb') as file:
                response = HttpResponse(file.read(), content_type=attachment.file_type)
                response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
                return response
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return Response({
                'success': False,
                'error': 'Error al leer el archivo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except DocumentAttachment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Adjunto no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error downloading supplier report attachment: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_supplier_report_attachment(request, attachment_id):
    """Visualiza un adjunto de reporte de proveedor en el navegador"""
    try:
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_type='supplier_report'
        )
        
        # Verificar permisos (por ahora todos los archivos son públicos)
        # if attachment.uploaded_by != request.user:
        #     return Response({
        #         'success': False,
        #         'error': 'No tienes permisos para acceder a este archivo'
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que el archivo existe
        if not attachment.file or not attachment.file.name:
            return Response({
                'success': False,
                'error': 'Archivo no encontrado en el servidor'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Leer archivo
        try:
            with attachment.file.open('rb') as file:
                response = HttpResponse(file.read(), content_type=attachment.file_type)
                response['Content-Disposition'] = f'inline; filename="{attachment.filename}"'
                return response
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return Response({
                'success': False,
                'error': 'Error al leer el archivo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except DocumentAttachment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Adjunto no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error viewing supplier report attachment: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_supplier_report_attachment(request, attachment_id):
    """Elimina un adjunto de reporte de proveedor"""
    try:
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_type='supplier_report'
        )
        
        # Verificar permisos (solo el creador puede eliminar)
        if attachment.uploaded_by != request.user:
            return Response({
                'success': False,
                'error': 'No tienes permisos para eliminar este archivo'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Eliminar archivo físico si existe
        if attachment.file and attachment.file.name:
            try:
                attachment.file.delete(save=False)
            except Exception as e:
                logger.warning(f"Error deleting physical file {attachment.file.name}: {e}")
        
        # Eliminar registro de la base de datos
        attachment.delete()
        
        return Response({
            'success': True,
            'message': 'Archivo eliminado exitosamente'
        })
        
    except DocumentAttachment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Adjunto no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting supplier report attachment: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_supplier_report_attachment_info(request, attachment_id):
    """Obtiene información detallada de un adjunto de reporte de proveedor"""
    try:
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_type='supplier_report'
        )
        
        # Verificar permisos (por ahora todos los archivos son públicos)
        # if attachment.uploaded_by != request.user:
        #     return Response({
        #         'success': False,
        #         'error': 'No tienes permisos para acceder a este archivo'
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar si el archivo existe físicamente
        file_exists = attachment.file and attachment.file.name and attachment.file.storage.exists(attachment.file.name)
        file_size = attachment.file_size if file_exists else 0
        
        return Response({
            'success': True,
            'attachment': {
                'id': attachment.id,
                'filename': attachment.filename,
                'title': attachment.filename,
                'description': attachment.description,
                'document_type': getattr(attachment, 'supplier_document_type', 'unknown'),
                'size': file_size,
                'mime_type': attachment.file_type,
                'created_at': attachment.uploaded_at,
                'created_by': attachment.uploaded_by.username if attachment.uploaded_by else 'Sistema',
                'is_public': True,
                'file_exists': file_exists,
                'file_path': attachment.file.name if attachment.file else None,
                'metadata': {}
            }
        })
        
    except DocumentAttachment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Adjunto no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting supplier report attachment info: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
