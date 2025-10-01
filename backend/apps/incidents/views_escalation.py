from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Incident
from .services.email_service import EmailService
import logging

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
        if incident.escalated_to_quality:
            return Response(
                {'error': 'La incidencia ya fue escalada a calidad'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar la incidencia
        incident.escalated_to_quality = True
        incident.escalation_date = timezone.now()
        incident.escalation_reason = request.data.get('reason', 'Escalado desde reporte de visita')
        incident.estado = 'laboratorio'  # Cambiar estado a laboratorio
        incident.save()
        
        # Buscar y adjuntar PDF del reporte de visita si existe
        visit_report_path = None
        try:
            from apps.documents.models import VisitReport
            from django.conf import settings
            import os
            
            # Buscar reporte de visita relacionado con la incidencia
            visit_report = VisitReport.objects.filter(related_incident=incident).first()
            
            if visit_report and visit_report.pdf_path:
                # Verificar que el archivo existe
                if os.path.exists(visit_report.pdf_path):
                    visit_report_path = visit_report.pdf_path
                    logger.info(f"PDF de reporte de visita encontrado: {visit_report_path}")
                else:
                    logger.warning(f"PDF de reporte de visita no encontrado en: {visit_report.pdf_path}")
            else:
                logger.info(f"No se encontró reporte de visita para la incidencia {incident.code}")
        except Exception as pdf_error:
            logger.warning(f"Error buscando PDF de reporte de visita: {str(pdf_error)}")
        
        # Intentar enviar correo de notificación (no crítico)
        email_sent = False
        try:
            email_service = EmailService()
            email_sent = email_service.send_escalation_to_quality_email(incident, visit_report_path)
            logger.info(f"Email de escalación enviado: {email_sent}")
        except Exception as email_error:
            logger.warning(f"Error enviando email de escalación: {str(email_error)}")
            # Continuar sin fallar por el email
        
        if email_sent:
            logger.info(f"Incidencia {incident.code} escalada a calidad exitosamente")
            return Response({
                'success': True,
                'message': 'Incidencia escalada a calidad exitosamente',
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
            {'error': f'Error escalando incidencia: {str(e)}'}, 
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
                'categoria': incident.get_categoria_display(),
                'subcategoria': incident.subcategoria,
                'prioridad': incident.get_prioridad_display(),
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
