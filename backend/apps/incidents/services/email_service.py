
import logging
import os
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de correos usando Django SMTP"""

    @staticmethod
    def send_email_with_attachment(subject, message, recipient_list, attachment_path=None, from_email=None, cc_list=None):
        """
        Envía un correo con archivo adjunto opcional.
        Retorna: (success: bool, error_message: str)
        """
        try:
            if not from_email:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@postventa.com')
                
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
                cc=cc_list or []
            )
            email.content_subtype = "html"  # Permitir HTML
            
            if attachment_path and os.path.exists(attachment_path):
                email.attach_file(attachment_path)
            elif attachment_path:
                logger.warning(f"Intento de adjuntar archivo inexistente: {attachment_path}")
            
            # Enviar
            email.send(fail_silently=False)
            logger.info(f"Correo enviado a {recipient_list} (CC: {cc_list}): {subject}")
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error enviando correo a {recipient_list}: {error_msg}", exc_info=True)
            return False, error_msg

    def send_escalation_to_quality_email(self, incident, visit_report_path=None):
        """
        Envía correo de escalamiento a calidad
        """
        # Destinatarios (MODO PRUEBA: Solo jdiaz)
        to_emails = ['jdiaz@polifusion.cl']
        cc_emails = []
        
        subject = f'[ESCALAMIENTO A CALIDAD] {incident.code} - {incident.cliente}'
        html_content = self._generate_quality_escalation_body(incident)
        
        success, _ = self.send_email_with_attachment(
            subject=subject,
            message=html_content,
            recipient_list=to_emails,
            cc_list=cc_emails,
            attachment_path=visit_report_path
        )
        return success
    
    def send_escalation_to_supplier_email(self, incident, quality_report_path=None):
        """
        Envía correo de escalamiento a proveedor
        """
        # Destinatarios (MODO PRUEBA: Solo jdiaz)
        to_emails = ['jdiaz@polifusion.cl']
        cc_emails = []
        
        subject = f'[ESCALAMIENTO A PROVEEDOR] {incident.code} - {incident.cliente}'
        html_content = self._generate_supplier_escalation_body(incident)
        
        success, _ = self.send_email_with_attachment(
            subject=subject,
            message=html_content,
            recipient_list=to_emails,
            cc_list=cc_emails,
            attachment_path=quality_report_path
        )
        return success
    
    def _generate_quality_escalation_body(self, incident):
        """Genera el cuerpo del correo de escalamiento a calidad"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; }}
                .content {{ padding: 20px; }}
                .incident-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ background-color: #e9ecef; padding: 15px; font-size: 12px; color: #6c757d; }}
                .highlight {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 ESCALAMIENTO A CALIDAD - INCIDENCIA {incident.code}</h2>
                <p><strong>Fecha:</strong> {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="content">
                <p>Estimado equipo de Calidad,</p>
                
                <p>Se ha escalado la siguiente incidencia para su análisis y evaluación:</p>
                
                <div class="incident-info">
                    <h3>📋 Información de la Incidencia</h3>
                    <p><strong>Código:</strong> {incident.code}</p>
                    <p><strong>Cliente:</strong> {incident.cliente}</p>
                    <p><strong>Proveedor:</strong> {incident.provider}</p>
                    <p><strong>Obra:</strong> {incident.obra}</p>
                    <p><strong>Categoría:</strong> {str(incident.categoria)}</p>
                    <p><strong>Subcategoría:</strong> {incident.subcategoria or 'N/A'}</p>
                    <p><strong>Responsable Técnico:</strong> {incident.responsable}</p>
                    <p><strong>Prioridad:</strong> <span class="highlight">{incident.prioridad}</span></p>
                </div>
                
                <div class="incident-info">
                    <h3>📝 Descripción del Problema</h3>
                    <p>{incident.descripcion}</p>
                </div>
                
                <p><strong>📎 Adjunto:</strong> Reporte de Visita Técnica (PDF)</p>
                
                <p><strong>🎯 Próximos Pasos:</strong></p>
                <ul>
                    <li>Revisar el reporte de visita adjunto</li>
                    <li>Analizar las muestras del producto</li>
                    <li>Determinar si se requiere análisis de laboratorio</li>
                </ul>
                
                <p>Por favor, mantengan informado al equipo técnico sobre el progreso del análisis.</p>
                
                <p>Saludos cordiales,<br>
                <strong>Equipo Técnico - Polifusion</strong></p>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático del Sistema de Gestión de Incidencias Polifusion</p>
                <p>Para consultas, contactar a: jdiaz@polifusion.cl</p>
            </div>
        </body>
        </html>
        """
    
    def _generate_supplier_escalation_body(self, incident):
        """Genera el cuerpo del correo de escalamiento a proveedor"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-left: 4px solid #28a745; }}
                .content {{ padding: 20px; }}
                .incident-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ background-color: #e9ecef; padding: 15px; font-size: 12px; color: #6c757d; }}
                .highlight {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📤 ESCALAMIENTO A PROVEEDOR - INCIDENCIA {incident.code}</h2>
                <p><strong>Fecha:</strong> {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="content">
                <p>Estimado equipo,</p>
                
                <p>Se ha escalado la siguiente incidencia al proveedor para su revisión y respuesta:</p>
                
                <div class="incident-info">
                    <h3>📋 Información de la Incidencia</h3>
                    <p><strong>Código:</strong> {incident.code}</p>
                    <p><strong>Cliente:</strong> {incident.cliente}</p>
                    <p><strong>Proveedor:</strong> {incident.provider}</p>
                    <p><strong>Obra:</strong> {incident.obra}</p>
                    <p><strong>Categoría:</strong> {str(incident.categoria)}</p>
                    <p><strong>Subcategoría:</strong> {incident.subcategoria or 'N/A'}</p>
                    <p><strong>Prioridad:</strong> <span class="highlight">{incident.prioridad}</span></p>
                </div>
                
                <div class="incident-info">
                    <h3>📝 Descripción del Problema</h3>
                    <p>{incident.descripcion}</p>
                </div>
                
                <p><strong>📎 Adjunto:</strong> Reporte de Calidad (PDF)</p>
                
                <p><strong>🎯 Próximos Pasos:</strong></p>
                <ul>
                    <li>Contactar al proveedor con la información adjunta</li>
                    <li>Solicitar análisis técnico del producto</li>
                    <li>Coordinar muestras para análisis de laboratorio si es necesario</li>
                    <li>Mantener seguimiento de la respuesta del proveedor</li>
                </ul>
                
                <p>Saludos cordiales,<br>
                <strong>Equipo de Calidad - Polifusion</strong></p>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático del Sistema de Gestión de Incidencias Polifusion</p>
                <p>Para consultas, contactar a: jdiaz@polifusion.cl</p>
            </div>
        </body>
        </html>
        """
