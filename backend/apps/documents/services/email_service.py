import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import os

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_visit_report(report, recipient_list=None):
        """
        Envía un correo profesional con el reporte de visita adjunto.
        """
        if not report.pdf_file:
            logger.error(f"Cannot send email: PDF file field is empty for report {report.report_number}")
            return False, "Archivo PDF no generado aún."
        
        # Verificar si el archivo existe físicamente
        if not report.pdf_file.storage.exists(report.pdf_file.name):
            logger.error(f"Cannot send email: PDF file {report.pdf_file.name} not found in storage.")
            return False, "Archivo PDF no encontrado físicamente."

        if not recipient_list:
            logger.error(f"Cannot send email: No recipients provided for report {report.report_number}")
            return False, "Debe proporcionar al menos un correo electrónico de destino."
        
        subject = f"Reporte de Visita Técnica {report.report_number} - {report.project_name}"
        
        # Cuerpo del correo profesional
        context = {
            'report_number': report.report_number,
            'client_name': report.client_name,
            'project_name': report.project_name,
            'visit_date': report.visit_date,
            'technician': report.technician,
            'year': timezone.now().year
        }
        
        # Mensaje simple si no hay template HTML (podemos mejorarlo luego)
        body = f"""
Estimado/a,

Se adjunta el Reporte de Visita Técnica {report.report_number} correspondiente a la visita realizada en la obra {report.project_name}.

Detalles de la Visita:
- Cliente: {report.client_name}
- Fecha: {report.visit_date}
- Técnico: {report.technician}

Este es un correo automático generado por Sertec Polifusion System. Por favor, no responda a este mensaje.

Atentamente,
Departamento de Postventa y Servicio Técnico
Polifusión S.A.
        """

        try:
            # Cuerpo del correo profesional usando template HTML
            html_content = render_to_string('emails/visit_report_email.html', context)
            
            email = EmailMessage(
                subject=subject,
                body=body, # Fallback plain text
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )
            email.content_subtype = "html" # Marcar como HTML
            email.body = html_content # Usar el contenido renderizado
            
            # Adjuntar el PDF
            try:
                report.pdf_file.open('rb')
                pdf_content = report.pdf_file.read()
                report.pdf_file.close()
                
                email.attach(
                    f"Reporte_{report.report_number}.pdf",
                    pdf_content,
                    'application/pdf'
                )
            except Exception as attachment_err:
                logger.error(f"Error attaching PDF: {attachment_err}")
                return False, f"Error al adjuntar PDF: {str(attachment_err)}"
            
            email.send(fail_silently=False)
            logger.info(f"Email sent successfully for report {report.report_number}")
            return True, "Correo enviado con éxito."
        except Exception as e:
            logger.error(f"Error sending email for report {report.report_number}: {e}")
            return False, str(e)
