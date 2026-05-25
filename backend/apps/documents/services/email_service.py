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

    @staticmethod
    def send_technician_notification(visit_id, is_new, date_changed, technician_changed):
        """
        Envía un correo electrónico profesional al técnico asignado cuando se programa
        o reprograma una visita técnica.
        """
        import logging
        import unicodedata
        from django.contrib.auth import get_user_model
        from apps.visits.models import VisitReport
        
        logger = logging.getLogger(__name__)
        
        try:
            # 1. Recuperar la visita actualizada
            visit = VisitReport.objects.get(id=visit_id)
            if not visit.technician:
                logger.info(f"No technician assigned to visit {visit.report_number}. Skipping email notification.")
                return False, "No hay técnico asignado."
                
            # 2. Buscar al usuario en Django que coincida con el técnico
            User = get_user_model()
            technician_user = None
            
            def clean_str(s):
                if not s: return ""
                return "".join(
                    c for c in unicodedata.normalize('NFD', s.lower())
                    if unicodedata.category(c) != 'Mn'
                ).strip()
                
            clean_tech = clean_str(visit.technician)
            if clean_tech:
                for u in User.objects.filter(is_active=True):
                    u_full = clean_str(f"{u.first_name} {u.last_name}")
                    u_username = clean_str(u.username)
                    if clean_tech == u_full or clean_tech == u_username or (len(clean_tech) > 3 and (clean_tech in u_full or u_full in clean_tech)):
                        technician_user = u
                        break
                        
            if not technician_user or not technician_user.email:
                logger.warning(f"Could not find a Django User with active email for technician '{visit.technician}'. Notification skipped.")
                return False, f"Técnico '{visit.technician}' no tiene usuario o email configurado en el sistema."
                
            # 3. Preparar asunto y contexto del correo
            is_reschedule = (not is_new) and (date_changed or technician_changed)
            
            if is_reschedule:
                subject = f"🔔 [REPROGRAMADA] Visita Técnica {visit.report_number} - Obra: {visit.project_name or 'Sin Nombre'}"
                greeting_msg = "Le informamos que la visita técnica que tiene asignada ha sido reprogramada."
            else:
                subject = f"📅 [NUEVA VISITA] Visita Técnica {visit.report_number} - Obra: {visit.project_name or 'Sin Nombre'}"
                greeting_msg = "Le informamos que se le ha asignado y programado una nueva visita técnica."
                
            # Formatear la fecha (SOLO FECHA, SIN HORA)
            try:
                formatted_date = timezone.localtime(visit.visit_date).strftime('%d/%m/%Y')
            except Exception:
                try:
                    formatted_date = visit.visit_date.strftime('%d/%m/%Y')
                except Exception:
                    formatted_date = str(visit.visit_date).split(' ')[0]
                
            # Determinar URL de la visita para el botón de acción
            domain = getattr(settings, 'FRONTEND_URL', 'https://sertec.polifusion.com')
            visit_url = f"{domain.rstrip('/')}/visit-reports/{visit.id}/edit"
            
            context = {
                'technician_name': technician_user.first_name or visit.technician,
                'is_reschedule': is_reschedule,
                'greeting_message': greeting_msg,
                'report_number': visit.report_number,
                'project_name': visit.project_name or 'No especificado',
                'client_name': visit.client_name or 'No especificado',
                'address': visit.address or 'No especificada',
                'commune': visit.commune or 'No especificada',
                'city': visit.city or 'Santiago',
                'visit_date': formatted_date,
                'salesperson': visit.salesperson or 'No asignado',
                'visit_url': visit_url,
                'year': timezone.now().year
            }
            
            # 4. Renderizar contenido
            html_content = render_to_string('emails/technician_notification_email.html', context)
            
            # Texto plano de fallback
            body = f"""
Estimado/a {context['technician_name']},

{greeting_msg}

Detalles de la Visita:
- Nº de Reporte: {context['report_number']}
- Fecha Visita: {context['visit_date']}
- Obra/Proyecto: {context['project_name']}
- Cliente: {context['client_name']}
- Dirección: {context['address']}
- Comuna: {context['commune']}, {context['city']}
- Vendedor: {context['salesperson']}

Puede ver y editar esta visita accediendo al siguiente enlace:
{visit_url}

Atentamente,
Departamento de Postventa y Servicio Técnico
Polifusión S.A.
            """
            
            # Enviar el correo (Redirigido temporalmente a jdiaz@polifusion.cl en pre-producción)
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['jdiaz@polifusion.cl'],
            )
            email.content_subtype = "html"
            email.body = html_content
            
            email.send(fail_silently=False)
            logger.info(f"Notification email successfully sent (Redirected to 'jdiaz@polifusion.cl' from '{technician_user.email}') for visit {visit.report_number}")
            return True, "Notificación enviada al técnico con éxito (Redirigida a jdiaz@polifusion.cl)."
            
        except Exception as e:
            logger.error(f"Error sending technician notification: {str(e)}")
            return False, str(e)

