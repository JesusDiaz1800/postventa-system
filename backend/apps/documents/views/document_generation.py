"""
Vistas para generar y gestionar documentos en la carpeta compartida
"""
import os
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
import logging

from ..models import VisitReport, LabReport, SupplierReport
from ..document_generator_service import DocumentGeneratorService

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_visit_report_document(request, report_id):
    """Generar documento PDF para un reporte de visita"""
    try:
        report = VisitReport.objects.get(id=report_id)
        
        # Generar PDF usando el servicio existente
        from ..pdf_service import PDFDocumentService
        pdf_service = PDFDocumentService()
        
        # Preparar datos para el PDF
        pdf_data = {
            'report_number': report.report_number,
            'fecha_visita': report.visit_date.strftime('%d/%m/%Y'),
            'cliente': report.client_name,
            'proyecto': report.project_name,
            'tecnico_responsable': report.technician,
            'tipo_visita': report.visit_reason,
            'detalles_visita': report.general_observations,
            'hallazgos': report.general_observations,
            'recomendaciones': report.general_observations,
            'proximos_pasos': report.general_observations,
            'incidencia': {
                'codigo': report.related_incident.incident_number if hasattr(report.related_incident, 'incident_number') else str(report.related_incident.id),
                'cliente': report.related_incident.client_name if hasattr(report.related_incident, 'client_name') else report.related_incident.cliente,
                'producto': report.related_incident.product_name if hasattr(report.related_incident, 'product_name') else 'Producto',
                'descripcion': report.related_incident.description if hasattr(report.related_incident, 'description') else '',
            }
        }
        
        # Generar PDF
        result = pdf_service.generate_polifusion_visit_report_pdf(pdf_data)
        
        if result['success']:
            # Actualizar el reporte con la ruta del PDF
            report.pdf_path = result['file_path']
            report.save()
            
            return Response({
                'success': True,
                'message': 'PDF generado exitosamente',
                'filename': result['filename'],
                'filepath': result['file_path']
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Error generando PDF')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except VisitReport.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Reporte de visita no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de visita: {e}")
        return Response({
            'success': False,
            'error': f'Error generando PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_lab_report_document(request, report_id):
    """Generar documento PDF para un informe de laboratorio"""
    try:
        report = LabReport.objects.get(id=report_id)
        
        # Generar PDF usando el servicio existente
        from ..pdf_service import PDFDocumentService
        pdf_service = PDFDocumentService()
        
        # Preparar datos para el PDF
        pdf_data = {
            'report_number': report.report_number,
            'fecha_solicitud': report.request_date.strftime('%d/%m/%Y'),
            'solicitante': report.applicant,
            'cliente': report.client,
            'proyecto': report.related_incident.obra or 'Proyecto',
            'descripcion': report.description,
            'incident_code': report.related_incident.code,
            'incidencia': {
                'codigo': report.related_incident.code,
                'cliente': report.related_incident.cliente,
                'sku': report.related_incident.sku,
                'lote': report.related_incident.lote,
            }
        }
        
        # Generar PDF
        result = pdf_service.generate_polifusion_lab_report_pdf(pdf_data)
        
        if result['success']:
            # Actualizar el reporte con la ruta del PDF
            report.pdf_path = result['file_path']
            report.save()
            
            return Response({
                'success': True,
                'message': 'PDF generado exitosamente',
                'filename': result['filename'],
                'filepath': result['file_path']
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Error generando PDF')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except LabReport.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Informe de laboratorio no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error generando PDF de informe de laboratorio: {e}")
        return Response({
            'success': False,
            'error': f'Error generando PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_supplier_report_document(request, report_id):
    """Generar documento PDF para un informe de proveedor"""
    try:
        report = SupplierReport.objects.get(id=report_id)
        
        # Generar PDF usando el servicio existente
        from ..pdf_service import PDFDocumentService
        pdf_service = PDFDocumentService()
        
        # Preparar datos para el PDF
        pdf_data = {
            'report_number': report.report_number,
            'fecha_reporte': report.report_date.strftime('%d/%m/%Y'),
            'proveedor': report.supplier_name,
            'contacto': report.supplier_contact,
            'email': report.supplier_email,
            'asunto': report.subject,
            'introduccion': report.introduction,
            'descripcion_problema': report.problem_description,
            'analisis_tecnico': report.technical_analysis,
            'recomendaciones': report.recommendations,
            'incident_code': report.related_incident.code,
            'incidencia': {
                'codigo': report.related_incident.code,
                'cliente': report.related_incident.cliente,
                'sku': report.related_incident.sku,
                'lote': report.related_incident.lote,
            }
        }
        
        # Generar PDF (usando incident report como base)
        result = pdf_service.generate_polifusion_incident_report_pdf(pdf_data)
        
        if result['success']:
            # Actualizar el reporte con la ruta del PDF
            report.pdf_path = result['file_path']
            report.save()
            
            return Response({
                'success': True,
                'message': 'PDF generado exitosamente',
                'filename': result['filename'],
                'filepath': result['file_path']
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Error generando PDF')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except SupplierReport.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Informe para proveedor no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error generando PDF de informe para proveedor: {e}")
        return Response({
            'success': False,
            'error': f'Error generando PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_pdf_document(request, document_id):
    """Servir un documento PDF desde la carpeta compartida"""
    try:
        # Buscar el documento por ID
        from ..models import VisitReport, LabReport, SupplierReport
        
        # Intentar encontrar en cada tipo de reporte
        report = None
        report_type = None
        
        try:
            report = VisitReport.objects.get(id=document_id)
            report_type = 'visit'
        except VisitReport.DoesNotExist:
            try:
                report = LabReport.objects.get(id=document_id)
                report_type = 'lab'
            except LabReport.DoesNotExist:
                try:
                    report = SupplierReport.objects.get(id=document_id)
                    report_type = 'supplier'
                except SupplierReport.DoesNotExist:
                    pass
        
        if not report or not report.pdf_path:
            return Response({
                'success': False,
                'error': 'Documento PDF no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Construir la URL del PDF
        pdf_url = f"/media/{report.pdf_path}"
        
        return Response({
            'success': True,
            'pdf_url': pdf_url,
            'filename': report.pdf_path.split('/')[-1],
            'report_type': report_type
        })
        
    except Exception as e:
        logger.error(f"Error sirviendo PDF: {e}")
        return Response({
            'success': False,
            'error': f'Error sirviendo PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def serve_pdf_public(request, document_id):
    """Servir un documento PDF públicamente (sin autenticación)"""
    try:
        logger.info(f"serve_pdf_public called with document_id: {document_id}")
        
        # Buscar el documento por ID
        from ..models import VisitReport, LabReport, SupplierReport
        
        # Intentar encontrar en cada tipo de reporte
        report = None
        report_type = None
        
        try:
            report = VisitReport.objects.get(id=document_id)
            report_type = 'visit'
            logger.info(f"Found VisitReport: {report.id}, pdf_path: {report.pdf_path}")
        except VisitReport.DoesNotExist:
            try:
                report = LabReport.objects.get(id=document_id)
                report_type = 'lab'
                logger.info(f"Found LabReport: {report.id}, pdf_path: {report.pdf_path}")
            except LabReport.DoesNotExist:
                try:
                    report = SupplierReport.objects.get(id=document_id)
                    report_type = 'supplier'
                    logger.info(f"Found SupplierReport: {report.id}, pdf_path: {report.pdf_path}")
                except SupplierReport.DoesNotExist:
                    logger.warning(f"No report found with id: {document_id}")
                    pass
        
        if not report:
            logger.error(f"Report not found for document_id: {document_id}")
            return Response({
                'success': False,
                'error': 'Documento no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not report.pdf_path:
            logger.error(f"PDF path not found for report: {report.id}")
            return Response({
                'success': False,
                'error': 'PDF no generado para este documento'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Construir la URL del PDF
        pdf_url = f"/media/{report.pdf_path}"
        logger.info(f"Returning PDF URL: {pdf_url}")
        
        return Response({
            'success': True,
            'pdf_url': pdf_url,
            'filename': report.pdf_path.split('/')[-1],
            'report_type': report_type
        })
        
    except Exception as e:
        logger.error(f"Error sirviendo PDF público: {e}")
        return Response({
            'success': False,
            'error': f'Error sirviendo PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_shared_documents(request):
    """Listar todos los documentos en la carpeta compartida"""
    try:
        generator = DocumentGeneratorService()
        document_type = request.GET.get('type')
        
        documents = generator.list_documents(document_type)
        
        # Formatear datos para la respuesta
        formatted_documents = []
        for doc in documents:
            formatted_documents.append({
                'type': doc['type'],
                'filename': doc['filename'],
                'size': doc['size'],
                'created': doc['created'].isoformat(),
                'modified': doc['modified'].isoformat(),
                'download_url': f'/api/documents/shared/{doc["type"]}/{doc["filename"]}/download/',
                'view_url': f'/api/documents/shared/{doc["type"]}/{doc["filename"]}/view/',
            })
        
        return Response({
            'success': True,
            'documents': formatted_documents,
            'total': len(formatted_documents)
        })
        
    except Exception as e:
        logger.error(f"Error listando documentos compartidos: {e}")
        return Response({
            'success': False,
            'error': f'Error listando documentos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shared_document(request, document_type, filename):
    """Descargar un documento de la carpeta compartida"""
    try:
        generator = DocumentGeneratorService()
        filepath = generator.get_document_path(document_type, filename)
        
        if not os.path.exists(filepath):
            return Response({
                'success': False,
                'error': 'Documento no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Determinar el tipo de contenido
        if filename.endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.endswith('.pdf'):
            content_type = 'application/pdf'
        else:
            content_type = 'application/octet-stream'
        
        response = FileResponse(
            open(filepath, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=filename
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error descargando documento: {e}")
        return Response({
            'success': False,
            'error': f'Error descargando documento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_shared_document(request, document_type, filename):
    """Visualizar un documento de la carpeta compartida"""
    try:
        generator = DocumentGeneratorService()
        filepath = generator.get_document_path(document_type, filename)
        
        if not os.path.exists(filepath):
            return Response({
                'success': False,
                'error': 'Documento no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Determinar el tipo de contenido
        if filename.endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.endswith('.pdf'):
            content_type = 'application/pdf'
        else:
            content_type = 'application/octet-stream'
        
        response = FileResponse(
            open(filepath, 'rb'),
            content_type=content_type,
            filename=filename
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error visualizando documento: {e}")
        return Response({
            'success': False,
            'error': f'Error visualizando documento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_shared_document(request, document_type, filename):
    """Eliminar un documento de la carpeta compartida"""
    try:
        generator = DocumentGeneratorService()
        
        success = generator.delete_document(document_type, filename)
        
        if success:
            return Response({
                'success': True,
                'message': 'Documento eliminado exitosamente'
            })
        else:
            return Response({
                'success': False,
                'error': 'Documento no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error eliminando documento: {e}")
        return Response({
            'success': False,
            'error': f'Error eliminando documento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_info(request, document_type, filename):
    """Obtener información detallada de un documento"""
    try:
        generator = DocumentGeneratorService()
        filepath = generator.get_document_path(document_type, filename)
        
        if not os.path.exists(filepath):
            return Response({
                'success': False,
                'error': 'Documento no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        stat = os.stat(filepath)
        
        return Response({
            'success': True,
            'document': {
                'type': document_type,
                'filename': filename,
                'filepath': filepath,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'download_url': f'/api/documents/shared/{document_type}/{filename}/download/',
                'view_url': f'/api/documents/shared/{document_type}/{filename}/view/',
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo información del documento: {e}")
        return Response({
            'success': False,
            'error': f'Error obteniendo información: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
