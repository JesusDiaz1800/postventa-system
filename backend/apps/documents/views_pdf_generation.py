"""
Vistas para generación de PDFs profesionales
"""
import os
import logging
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import VisitReport, LabReport, SupplierReport
from .pdf_generator_professional import ProfessionalPDFGenerator

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_visit_report_pdf(request, report_id):
    """
    Genera PDF profesional para reporte de visita
    """
    try:
        report = VisitReport.objects.get(id=report_id)
        
        # Crear generador de PDF
        pdf_generator = ProfessionalPDFGenerator()
        
        # Preparar datos para el PDF
        report_data = {
            'report_number': report.report_number,
            'visit_date': report.visit_date.strftime('%d/%m/%Y') if report.visit_date else '',
            'client_name': report.client_name or '',
            'project_name': report.project_name or '',
            'address': report.address or '',
            'salesperson': report.salesperson or '',
            'technician': report.technician or '',
            'commune': report.commune or '',
            'city': report.city or '',
            'visit_reason': report.visit_reason or '',
            'general_observations': report.general_observations or '',
            'incident': {
                'codigo': report.related_incident.code if report.related_incident else '',
                'cliente': report.related_incident.cliente if report.related_incident else '',
                'producto': report.related_incident.sku if report.related_incident else '',
                'descripcion': report.related_incident.descripcion if report.related_incident else '',
            } if report.related_incident else None
        }
        
        # Crear directorio si no existe
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_path:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        incident_id = report.related_incident.id if report.related_incident else report.id
        output_dir = os.path.join(shared_path, 'visit_report', f'incident_{incident_id}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre del archivo
        filename = f"{report.report_number}_Reporte_Visita.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Generar PDF
        success = pdf_generator.create_visit_report_pdf(report_data, output_path)
        
        if success:
            # Actualizar el reporte con la ruta del PDF
            report.pdf_path = output_path
            report.save()
            
            # Retornar el archivo
            return FileResponse(open(output_path, 'rb'), as_attachment=False)
        else:
            return Response(
                {'error': 'Error generando PDF'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except VisitReport.DoesNotExist:
        return Response(
            {'error': 'Reporte no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de visita: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_lab_report_pdf(request, report_id):
    """
    Genera PDF profesional para reporte de laboratorio
    """
    try:
        report = LabReport.objects.get(id=report_id)
        
        # Crear generador de PDF
        pdf_generator = ProfessionalPDFGenerator()
        
        # Preparar datos para el PDF
        report_data = {
            'report_number': report.report_number,
            'form_number': report.form_number or '',
            'request_date': report.request_date.strftime('%d/%m/%Y') if report.request_date else '',
            'applicant': report.applicant or '',
            'client': report.client or '',
            'description': report.description or '',
            'project_background': report.project_background or '',
            'tests_performed': report.tests_performed or {},
            'comments': report.comments or '',
            'conclusions': report.conclusions or '',
            'recommendations': report.recommendations or '',
            'report_type': getattr(report, 'report_type', 'cliente'),
        }
        
        # Crear directorio si no existe
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_path:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        incident_id = report.related_incident.id if report.related_incident else report.id
        output_dir = os.path.join(shared_path, 'lab_report', f'incident_{incident_id}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre del archivo
        report_type_suffix = 'Cliente' if getattr(report, 'report_type', 'cliente') == 'cliente' else 'Interno'
        filename = f"{report.report_number}_Informe_{report_type_suffix}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Generar PDF
        success = pdf_generator.create_lab_report_pdf(report_data, output_path)
        
        if success:
            # Actualizar el reporte con la ruta del PDF
            report.pdf_path = output_path
            report.save()
            
            # Retornar el archivo
            return FileResponse(open(output_path, 'rb'), as_attachment=False)
        else:
            return Response(
                {'error': 'Error generando PDF'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except LabReport.DoesNotExist:
        return Response(
            {'error': 'Reporte no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de laboratorio: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_supplier_report_pdf(request, report_id):
    """
    Genera PDF profesional para reporte de proveedor
    """
    try:
        report = SupplierReport.objects.get(id=report_id)
        
        # Crear generador de PDF
        pdf_generator = ProfessionalPDFGenerator()
        
        # Preparar datos para el PDF
        report_data = {
            'report_number': report.report_number,
            'supplier_name': report.supplier_name or '',
            'supplier_contact': report.supplier_contact or '',
            'supplier_email': report.supplier_email or '',
            'subject': report.subject or '',
            'introduction': report.introduction or '',
            'problem_description': report.problem_description or '',
            'technical_analysis': report.technical_analysis or '',
            'recommendations': report.recommendations or '',
            'expected_improvements': report.expected_improvements or '',
            'report_date': report.report_date.strftime('%d/%m/%Y') if report.report_date else '',
        }
        
        # Crear directorio si no existe
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
        if not shared_path:
            return Response(
                {'error': 'Carpeta compartida no configurada'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        incident_id = report.related_incident.id if report.related_incident else report.id
        output_dir = os.path.join(shared_path, 'supplier_report', f'incident_{incident_id}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre del archivo
        filename = f"{report.report_number}_Evaluacion_Proveedor.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Generar PDF
        success = pdf_generator.create_supplier_report_pdf(report_data, output_path)
        
        if success:
            # Actualizar el reporte con la ruta del PDF
            report.pdf_path = output_path
            report.save()
            
            # Retornar el archivo
            return FileResponse(open(output_path, 'rb'), as_attachment=False)
        else:
            return Response(
                {'error': 'Error generando PDF'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except SupplierReport.DoesNotExist:
        return Response(
            {'error': 'Reporte no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
