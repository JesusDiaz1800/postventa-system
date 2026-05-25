"""
Vistas para gestión de adjuntos de reportes de visita
Permite subir, listar, descargar y ver archivos adjuntos
"""
import os
import mimetypes
import base64
from django.http import FileResponse
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.documents.models import DocumentAttachment
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_report_attachments(request, report_id, report_type):
    """
    Lista todos los adjuntos de un reporte
    """
    try:
        # Map report_type to document_type
        doc_type_map = {
            'visit': 'visit_report',
            'lab': 'lab_report',
            'supplier': 'supplier_report'
        }
        doc_type = doc_type_map.get(report_type, 'visit_report')
        
        attachments = DocumentAttachment.objects.filter(
            document_id=report_id,
            document_type=doc_type
        ).order_by('-uploaded_at')
        
        attachments_data = []
        for att in attachments:
            attachments_data.append({
                'id': att.id,
                'filename': att.filename,
                'file_type': att.file_type,
                'file_size': att.file_size,
                'description': att.description,
                'uploaded_at': att.uploaded_at,
                'uploaded_by': att.uploaded_by.username if att.uploaded_by else 'Sistema',
                'content_type': mimetypes.guess_type(att.filename)[0] or 'application/octet-stream',
                # Build URL for viewing
                'view_url': f'/documents/report-attachments/{report_id}/{report_type}/{att.id}/view/',
            })
        
        return Response(attachments_data)
        
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
    Sube archivos adjuntos a un reporte
    """
    try:
        if 'file' not in request.FILES and 'files' not in request.FILES:
            return Response(
                {'error': 'No se proporcionó ningún archivo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map report_type
        doc_type_map = {
            'visit': 'visit_report',
            'lab': 'lab_report',
            'supplier': 'supplier_report'
        }
        doc_type = doc_type_map.get(report_type, 'visit_report')
        
        # Handle single or multiple files
        files = request.FILES.getlist('files') or [request.FILES.get('file')]
        
        uploaded = []
        for file in files:
            if not file:
                continue
                
            # Determine file type
            file_type = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
            
            # Create the attachment record
            attachment = DocumentAttachment.objects.create(
                document_type=doc_type,
                document_id=report_id,
                file=file,
                filename=file.name,
                file_type=file_type,
                file_size=file.size,
                description=request.data.get('description', ''),
                uploaded_by=request.user
            )
            
            uploaded.append({
                'id': attachment.id,
                'filename': attachment.filename,
                'file_size': attachment.file_size,
                'file_type': attachment.file_type,
            })
            
        # If this is a visit report, regenerate the PDF to include the images
        if doc_type == 'visit_report' and uploaded:
            try:
                from apps.visits.models import VisitReport
                from apps.documents.services.professional_pdf_generator import ProfessionalPDFGenerator
                
                report = VisitReport.objects.get(id=report_id)
                
                # Fetch all images
                images = []
                attachments = DocumentAttachment.objects.filter(
                    document_id=report.id,
                    document_type='visit_report'
                ).exclude(file='').order_by('uploaded_at')
                
                for att in attachments:
                    if att.file and os.path.exists(att.file.path):
                        ext = os.path.splitext(att.filename)[1].lower()
                        if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                            images.append({
                                'path': att.file.path,
                                'description': att.description or att.filename
                            })
                
                # Prepare data for PDF
                pdf_data = {
                    'order_number': report.order_number,
                    'client_name': report.client_name,
                    'client_rut': report.client_rut,
                    'client_contact': getattr(report, 'client_contact', ''), # Asegurar contacto
                    'telephone': getattr(report, 'telephone', ''),
                    'project_name': report.project_name,
                    'project_id': report.project_id,
                    'address': report.address,
                    'commune': getattr(report, 'commune', ''),
                    'city': getattr(report, 'city', ''),
                    'visit_date': report.visit_date.strftime('%d/%m/%Y') if report.visit_date else '',
                    'salesperson': report.salesperson,
                    'technician': report.technician,
                    'construction_company': report.construction_company,
                    'installer': report.installer,
                    'installer_phone': report.installer_phone,
                    'product_category': getattr(report, 'product_category', ''),
                    'product_subcategory': getattr(report, 'product_subcategory', ''),
                    'visit_reason': report.visit_reason,
                    'general_observations': report.general_observations,
                    'wall_observations': report.wall_observations,
                    'matrix_observations': report.matrix_observations,
                    'slab_observations': report.slab_observations,
                    'storage_observations': report.storage_observations,
                    'pre_assembled_observations': report.pre_assembled_observations,
                    'exterior_observations': report.exterior_observations,
                    'machine_data': report.machine_data,
                    'status': report.get_status_display(),
                    'images': images
                }
                
                # Generate PDF
                pdf_generator = ProfessionalPDFGenerator()
                
                # Determine path using country code from the creator or default
                country = getattr(report.created_by, 'country_code', 'CL') if report.created_by else 'CL'
                report_folder = os.path.join(getattr(settings, 'MEDIA_ROOT', ''), 'documentos', country, 'visit_reports')
                os.makedirs(report_folder, exist_ok=True)
                pdf_path = os.path.join(report_folder, f"{report.report_number}.pdf")
                
                success = pdf_generator.generate_visit_report_pdf(pdf_data, pdf_path)
                
                if success and os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as f:
                        pdf_bytes = f.read()
                    report.pdf_file.save(f"{report.report_number}.pdf", ContentFile(pdf_bytes), save=False)
                    report.save(update_fields=['pdf_file'])
                    logger.info(f"PDF regenerado automáticamente con imágenes en SERTEC: {pdf_path}")
                    
            except Exception as e:
                logger.error(f"Error regenerando PDF tras subida de imagen: {e}")
        
        return Response({
            'message': f'{len(uploaded)} archivo(s) subido(s) exitosamente',
            'attachments': uploaded
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error uploading report attachment: {str(e)}")
        return Response(
            {'error': f'Error al subir archivo: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report_attachment(request, report_id, report_type, attachment_id):
    """
    Descarga un archivo adjunto
    """
    try:
        doc_type_map = {
            'visit': 'visit_report',
            'lab': 'lab_report',
            'supplier': 'supplier_report'
        }
        doc_type = doc_type_map.get(report_type, 'visit_report')
        
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_id=report_id,
            document_type=doc_type
        )
        
        if not attachment.file or not os.path.exists(attachment.file.path):
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(
            open(attachment.file.path, 'rb'),
            as_attachment=True,
            filename=attachment.filename
        )
        return response
        
    except DocumentAttachment.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error downloading attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_report_attachment(request, report_id, report_type, attachment_id):
    """
    Visualiza un archivo adjunto en el navegador (para imágenes y PDFs)
    """
    try:
        doc_type_map = {
            'visit': 'visit_report',
            'lab': 'lab_report',
            'supplier': 'supplier_report'
        }
        doc_type = doc_type_map.get(report_type, 'visit_report')
        
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_id=report_id,
            document_type=doc_type
        )
        
        if not attachment.file or not os.path.exists(attachment.file.path):
            return Response(
                {'error': 'Archivo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine content type
        content_type = attachment.file_type or mimetypes.guess_type(attachment.filename)[0] or 'application/octet-stream'
        
        response = FileResponse(
            open(attachment.file.path, 'rb'),
            content_type=content_type
        )
        # Add header for inline display (not download)
        response['Content-Disposition'] = f'inline; filename="{attachment.filename}"'
        return response
        
    except DocumentAttachment.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error viewing attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_report_attachment(request, report_id, report_type, attachment_id):
    """
    Elimina un archivo adjunto
    """
    try:
        doc_type_map = {
            'visit': 'visit_report',
            'lab': 'lab_report',
            'supplier': 'supplier_report'
        }
        doc_type = doc_type_map.get(report_type, 'visit_report')
        
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_id=report_id,
            document_type=doc_type
        )
        
        # Delete physical file
        if attachment.file and os.path.exists(attachment.file.path):
            os.remove(attachment.file.path)
        
        attachment.delete()
        
        return Response({'message': 'Adjunto eliminado exitosamente'})
        
    except DocumentAttachment.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting attachment: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_attachment_info(request, report_id, report_type, attachment_id):
    """
    Obtiene información detallada de un adjunto
    """
    try:
        doc_type_map = {
            'visit': 'visit_report',
            'lab': 'lab_report',
            'supplier': 'supplier_report'
        }
        doc_type = doc_type_map.get(report_type, 'visit_report')
        
        attachment = DocumentAttachment.objects.get(
            id=attachment_id,
            document_id=report_id,
            document_type=doc_type
        )
        
        return Response({
            'id': attachment.id,
            'filename': attachment.filename,
            'file_type': attachment.file_type,
            'file_size': attachment.file_size,
            'description': attachment.description,
            'uploaded_at': attachment.uploaded_at,
            'uploaded_by': attachment.uploaded_by.username if attachment.uploaded_by else 'Sistema',
            'file_exists': bool(attachment.file) and os.path.exists(attachment.file.path) if attachment.file else False
        })
        
    except DocumentAttachment.DoesNotExist:
        return Response(
            {'error': 'Adjunto no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting attachment info: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
