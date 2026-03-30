from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Incident, IncidentTimeline
from .services.email_service import EmailService
from django.db import models
import logging
import traceback

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def escalate_to_quality(request, incident_id):
    """
    Escala una incidencia a calidad
    """
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        
        # Validar que la incidencia no esté ya escalada
        # if incident.escalated_to_quality:
        #     return Response(
        #         {'error': 'La incidencia ya fue escalada a calidad'}, 
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # Actualizar la incidencia
        incident.escalated_to_quality = True
        # Keep original date if allowing re-escalation, or update? usually update is fine to show latest activity.
        incident.escalation_date = timezone.now()
        incident.escalation_reason = request.data.get('reason', incident.escalation_reason or 'Escalado desde reporte de visita')
        incident.estado = 'laboratorio'  # Cambiar estado a laboratorio
        incident.save()
        
        # Log timeline (Non-blocking)
        try:
            IncidentTimeline.objects.create(
                incident=incident,
                action='status_changed',
                description=f'Incidencia escalada a Calidad por {request.user.full_name if hasattr(request.user, "full_name") else request.user.username}',
                user=request.user
            )
        except Exception as log_error:
            logger.error(f"Error creating timeline log: {log_error}")
        
        # Datos de correo personalizados
        custom_subject = request.data.get('subject')
        custom_message = request.data.get('message')
        # extra_files es lista de archivos, request.FILES es donde vienen
        extra_files = request.FILES.getlist('attachments') if request.FILES else []

        # Buscar y adjuntar PDF del reporte de visita si existe
        visit_report_path = None
        try:
            from apps.documents.models import VisitReport
            from django.conf import settings
            import os
            
            # Buscar reporte de visita relacionado con la incidencia
            visit_report_id = request.data.get('visit_report_id')
            if visit_report_id:
                visit_report = VisitReport.objects.filter(id=visit_report_id, related_incident=incident).first()
            else:
                visit_report = VisitReport.objects.filter(related_incident=incident).first()
            
            if visit_report:
                # 1. Priorizar pdf_file.path (FileField) que es el estándar actual
                if visit_report.pdf_file and os.path.exists(visit_report.pdf_file.path):
                    visit_report_path = visit_report.pdf_file.path
                    logger.info(f"PDF de reporte de visita (file) encontrado: {visit_report_path}")
                # 2. Fallback a pdf_path (CharField) para compatibilidad
                elif visit_report.pdf_path and os.path.exists(visit_report.pdf_path):
                    visit_report_path = visit_report.pdf_path
                    logger.info(f"PDF de reporte de visita (path) encontrado: {visit_report_path}")
                else:
                    logger.warning(f"No se encontró archivo PDF físico en pdf_file ni en pdf_path para {visit_report.report_number}")
            else:
                logger.info(f"No se encontró reporte de visita para la incidencia {incident.code}")
        except Exception as pdf_error:
            logger.warning(f"Error buscando PDF de reporte de visita: {str(pdf_error)}")
        
        
        # Enviar correo de notificación usando EmailService centralizado
        email_sent = False
        try:
            email_service = EmailService()
            # Pasar la ruta del reporte de visita si existe
            email_sent = email_service.send_escalation_to_quality_email(
                incident=incident,
                visit_report_path=visit_report_path
            )
            
            if email_sent:
                logger.info(f"Correo de escalamiento enviado vía EmailService a los responsables de Calidad.")
            else:
                logger.warning(f"EmailService falló al enviar el correo para {incident.code}")
                
        except Exception as email_err:
            logger.error(f"Error crítico en EmailService: {str(email_err)}")
            email_sent = False
        
        if email_sent:
            logger.info(f"Incidencia {incident.code} escalada a calidad exitosamente y notificada por correo.")
            return Response({
                'success': True,
                'message': 'Incidencia escalada a calidad y correo enviado exitosamente a los responsables.',
                'incident': {
                    'id': incident.id,
                    'code': incident.code,
                    'escalated_to_quality': incident.escalated_to_quality,
                    'escalation_date': incident.escalation_date,
                    'estado': incident.estado
                }
            })
        else:
            # Aunque el correo falle, el escalamiento se registra
            logger.warning(f"Incidencia {incident.code} escalada pero correo no enviado")
            return Response({
                'success': True,
                'message': 'Incidencia escalada a calidad, pero hubo un problema enviando el correo',
                'incident': {
                    'id': incident.id,
                    'code': incident.code,
                    'escalated_to_quality': incident.escalated_to_quality,
                    'escalation_date': incident.escalation_date,
                    'estado': incident.estado
                }
            })
            
    except Exception as e:
        logger.error(f"Error escalando incidencia a calidad: {str(e)}")
        return Response(
            {'error': f'Error escalando incidencia: {str(e)}', 'detail': traceback.format_exc()}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def escalate_to_supplier(request, incident_id):
    """
    Escala una incidencia a proveedor
    """
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        
        # Validar que la incidencia esté escalada a calidad
        if not incident.escalated_to_quality:
            return Response(
                {'error': 'La incidencia debe estar escalada a calidad primero'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que no esté ya escalada a proveedor
        if incident.escalated_to_supplier:
            return Response(
                {'error': 'La incidencia ya fue escalada a proveedor'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar la incidencia
        incident.escalated_to_supplier = True
        incident.escalation_date = timezone.now()
        incident.escalation_reason = request.data.get('reason', 'Escalado desde reporte de calidad')
        incident.estado = 'propuesta'  # Cambiar estado a propuesta
        incident.save()
        
        # Log timeline (Non-blocking)
        try:
            IncidentTimeline.objects.create(
                incident=incident,
                action='status_changed',
                description=f'Incidencia escalada a Proveedor por {request.user.full_name if hasattr(request.user, "full_name") else request.user.username}',
                user=request.user
            )
        except Exception as log_error:
            logger.error(f"Error creating timeline log: {log_error}")
        
        # Enviar correo de notificación
        email_service = EmailService()
        
        # Obtener ruta del reporte de calidad si existe
        quality_report_path = None
        # Aquí deberías obtener la ruta del PDF del reporte de calidad
        # quality_report_path = get_quality_report_path(incident)
        
        # Enviar correo
        email_sent = email_service.send_escalation_to_supplier_email(incident, quality_report_path)
        
        if email_sent:
            logger.info(f"Incidencia {incident.code} escalada a proveedor exitosamente")
            return Response({
                'success': True,
                'message': 'Incidencia escalada a proveedor exitosamente',
                'incident': {
                    'id': incident.id,
                    'code': incident.code,
                    'escalated_to_supplier': incident.escalated_to_supplier,
                    'escalation_date': incident.escalation_date,
                    'estado': incident.estado
                }
            })
        else:
            # Aunque el correo falle, el escalamiento se registra
            logger.warning(f"Incidencia {incident.code} escalada pero correo no enviado")
            return Response({
                'success': True,
                'message': 'Incidencia escalada a proveedor, pero hubo un problema enviando el correo',
                'incident': {
                    'id': incident.id,
                    'code': incident.code,
                    'escalated_to_supplier': incident.escalated_to_supplier,
                    'escalation_date': incident.escalation_date,
                    'estado': incident.estado
                }
            })
            
    except Exception as e:
        logger.error(f"Error escalando incidencia a proveedor: {str(e)}")
        return Response(
            {'error': f'Error escalando incidencia: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_incident(request, incident_id):
    """
    Cierra una incidencia
    """
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        
        # Validar que la incidencia no esté ya cerrada
        if incident.estado == 'cerrado':
            return Response(
                {'error': 'La incidencia ya está cerrada'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cerrar la incidencia
        incident.estado = 'cerrado'
        incident.closed_by = request.user
        incident.closed_at = timezone.now()
        incident.fecha_cierre = timezone.now().date()
        incident.save()
        
        # Log timeline (Non-blocking)
        try:
            IncidentTimeline.objects.create(
                incident=incident,
                action='closed',
                description=f'Incidencia cerrada por {request.user.full_name if hasattr(request.user, "full_name") else request.user.username}',
                user=request.user
            )
        except Exception as log_error:
            logger.error(f"Error creating timeline log: {log_error}")
        
        logger.info(f"Incidencia {incident.code} cerrada por {request.user.username}")
        return Response({
            'success': True,
            'message': 'Incidencia cerrada exitosamente',
            'incident': {
                'id': incident.id,
                'code': incident.code,
                'estado': incident.estado,
                'closed_at': incident.closed_at,
                'closed_by': incident.closed_by.username if incident.closed_by else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error cerrando incidencia: {str(e)}")
        return Response(
            {'error': f'Error cerrando incidencia: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_escalated_incidents(request):
    """
    Obtiene incidencias escaladas a calidad para reportes de calidad
    """
    try:
        escalated_incidents = Incident.objects.filter(
            escalated_to_quality=True,
            estado__in=['laboratorio', 'en_progreso']
        ).exclude(
            escalated_to_supplier=True
        ).order_by('-escalation_date')
        
        incidents_data = []
        for incident in escalated_incidents:
            incidents_data.append({
                'id': incident.id,
                'code': incident.code,
                'cliente': incident.cliente,
                'provider': incident.provider,
                'categoria': incident.categoria.name if incident.categoria else None,
                'subcategoria': incident.subcategoria,
                'prioridad': incident.prioridad,
                'estado': incident.get_estado_display(),
                'escalation_date': incident.escalation_date,
                'escalation_reason': incident.escalation_reason
            })
        
        return Response({
            'success': True,
            'incidents': incidents_data,
            'count': len(incidents_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo incidencias escaladas: {str(e)}")
        return Response(
            {'error': f'Error obteniendo incidencias: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reopen_incident(request, incident_id):
    """
    Reabre una incidencia cerrada
    """
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        
        # Validar que la incidencia esté cerrada
        if incident.estado != 'cerrado':
            return Response(
                {'error': 'La incidencia no está cerrada'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reabrir la incidencia
        incident.estado = 'abierto'
        incident.closed_by = None
        incident.closed_at = None
        incident.fecha_cierre = None
        incident.save()
        
        # Log timeline (Non-blocking)
        try:
            IncidentTimeline.objects.create(
                incident=incident,
                action='reopened',
                description=f'Incidencia reabierta por {request.user.full_name if hasattr(request.user, "full_name") else request.user.username}',
                user=request.user
            )
        except Exception as log_error:
            logger.error(f"Error creating timeline log: {log_error}")
        
        logger.info(f"Incidencia {incident.code} reabierta por {request.user.username}")
        return Response({
            'success': True,
            'message': 'Incidencia reabierta exitosamente',
            'incident': {
                'id': incident.id,
                'code': incident.code,
                'estado': incident.estado,
                'reopened_at': timezone.now(),
                'reopened_by': request.user.username
            }
        })
        
    except Exception as e:
        logger.error(f"Error reabriendo incidencia: {str(e)}")
        return Response(
            {'error': f'Error reabriendo incidencia: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def escalated_incidents(request):
    """
    Obtiene incidencias escaladas con filtros opcionales
    """
    try:
        # Parámetros de filtro
        without_quality_report = request.GET.get('without_quality_report', 'false').lower() == 'true'
        report_type = request.GET.get('report_type', '')
        escalated_to_internal = request.GET.get('escalated_to_internal', 'false').lower() == 'true'
        
        # Query base
        if escalated_to_internal:
            incidents = Incident.objects.filter(escalated_to_internal_quality=True).select_related('categoria')
        else:
            incidents = Incident.objects.filter(escalated_to_quality=True).select_related('categoria')
        
        # Aplicar filtros
        if without_quality_report:
            # Filtrar incidencias que no tienen reporte de calidad del tipo solicitado
            # Si estamos buscando incidencias para reportes internos, solo excluir si ya tienen reporte interno
            if escalated_to_internal:
                 incidents = incidents.exclude(
                    quality_reports__report_type='interno'
                )
            elif report_type:
                incidents = incidents.exclude(
                    quality_reports__report_type=report_type
                )
            else:
                 # Default behavior: exclude if ANY report exists (unless we can infer type)
                 # Si no se especifica tipo, y no es escalacion interna, asumimos que se busca para reporte cliente
                 # Pero para seguridad, mantenemos el comportamiento de excluir si tiene algun reporte
                 # Solo si no es el caso de internal
                 incidents = incidents.exclude(
                    quality_reports__isnull=False
                 )
        
        if report_type:
            # Filtrar por tipo de reporte si es necesario
            if report_type == 'cliente':
                # Permitir incidencias escaladas desde cualquier estado si tienen el flag active
                pass
            elif report_type == 'interno':
                incidents = incidents.filter(escalated_to_internal_quality=True)
        
        # Ordenar por fecha de escalación
        incidents = incidents.order_by('-escalation_date')
        
        # Serializar datos
        incidents_data = []
        for incident in incidents:
            try:
                # Safe access to fields
                cat_name = incident.categoria.name if incident.categoria else None
                
                # Handle priority safely
                priority = getattr(incident, 'prioridad', 'media')
                if callable(priority): # In case it's a method
                    priority = priority()
                    
                # Handle status safely
                if hasattr(incident, 'get_estado_display'):
                    status_display = incident.get_estado_display()
                else:
                    status_display = getattr(incident, 'estado', 'Desconocido')

                incidents_data.append({
                    'id': incident.id,
                    'code': incident.code,
                    'cliente': incident.cliente,
                    'provider': incident.provider,
                    'categoria': cat_name,
                    'subcategoria': incident.subcategoria,
                    'prioridad': priority,
                    'estado': status_display,
                    'escalation_date': incident.escalation_date,
                    'escalation_reason': incident.escalation_reason,
                    'has_quality_report': incident.quality_reports.exists()
                })
            except Exception as item_error:
                logger.error(f"Error serializing incident {incident.id}: {str(item_error)}")
                continue

        return Response({
            'success': True,
            'incidents': incidents_data,
            'count': len(incidents_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo incidencias escaladas: {str(e)}")
        return Response(
            {'error': f'Error obteniendo incidencias: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Backwards compatibility alias
# Some existing URLs refer to `escalate_incident`; make it an alias to the
# current `escalate_to_quality` view so we don't break existing routes.
try:
    escalate_incident = escalate_to_quality
except NameError:
    # If escalate_to_quality isn't defined (unexpected), skip aliasing.
    pass
