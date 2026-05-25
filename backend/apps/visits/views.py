from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import VisitReport
from .serializers import VisitReportSerializer
import logging

logger = logging.getLogger(__name__)

class VisitReportListView(generics.ListCreateAPIView):
    queryset = VisitReport.objects.all()
    serializer_class = VisitReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'client_rut', 'salesperson', 'technician']
    search_fields = ['report_number', 'project_name', 'client_name', 'client_rut', 'address', 'visit_reason']
    ordering_fields = ['created_at', 'visit_date', 'report_number']
    ordering = ['-created_at']

class VisitReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VisitReport.objects.all()
    serializer_class = VisitReportSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_visit_pdf(request, pk):
    """
    Endpoint para generar el PDF del reporte de visita.
    Soporta modo preliminar (sin guardar ruta) y final.
    """
    try:
        report = get_object_or_404(VisitReport, pk=pk)
        is_final = request.data.get('final', False)
        client_signature = request.data.get('client_signature')
        
        # Si se envía firma del cliente, la guardamos
        if client_signature:
            report.client_signature = client_signature
            report.save()
            
        # Preparar datos para el generador
        from apps.documents.services.professional_pdf_generator import ProfessionalPDFGenerator
        import io
        
        generator = ProfessionalPDFGenerator()
        buffer = io.BytesIO()
        
        # Serializar datos para el generador (incluyendo adjuntos y firmas)
        serializer = VisitReportSerializer(report, context={'request': request})
        data = serializer.data
        
        # Inyectar firma del técnico si existe en el perfil del técnico asignado o del creador (si coinciden)
        technician_user = None
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Intentar buscar por nombre del técnico primero
        import unicodedata
        def clean_str(s):
            if not s: return ""
            return "".join(
                c for c in unicodedata.normalize('NFD', s.lower())
                if unicodedata.category(c) != 'Mn'
            ).strip()
            
        tech_name = report.technician
        clean_tech = clean_str(tech_name)
        
        if clean_tech:
            for u in User.objects.filter(is_active=True):
                u_full = clean_str(f"{u.first_name} {u.last_name}")
                u_username = clean_str(u.username)
                if clean_tech == u_full or clean_tech == u_username or (len(clean_tech) > 3 and (clean_tech in u_full or u_full in clean_tech)):
                    technician_user = u
                    break
                    
        # Si no se encontró por nombre pero coincide con creador (o el técnico está vacío)
        if not technician_user and report.created_by:
            creator_full = clean_str(f"{report.created_by.first_name} {report.created_by.last_name}")
            creator_username = clean_str(report.created_by.username)
            if not clean_tech or clean_tech == creator_full or clean_tech == creator_username:
                technician_user = report.created_by
                
        # Inyectar path si se resolvió el usuario y tiene firma
        if technician_user and hasattr(technician_user, 'digital_signature') and technician_user.digital_signature:
            data['technician_signature_path'] = technician_user.digital_signature.path

            
        success = generator.generate_visit_report_pdf(data, buffer)
        
        if success:
            # Resetear el puntero para la respuesta
            buffer.seek(0)
            
            filename = f"Reporte_{report.report_number}.pdf"
            if is_final:
                # Guardar el archivo en el modelo si es la versión final
                from django.core.files.base import ContentFile
                from .models import VisitStatus
                # Asegurar puntero al inicio
                buffer.seek(0)
                # Guardamos el archivo
                report.pdf_file.save(filename, ContentFile(buffer.read()), save=False)
                # Actualizamos el estado a APPROVED
                report.status = VisitStatus.APPROVED
                # Al hacer save(), el modelo ejecutará la lógica de SAP Sync
                report.save()
                
                buffer.seek(0)
            
            from django.http import HttpResponse
            response = HttpResponse(buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            return Response({"error": "Error generando PDF interno"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"FATAL ERROR en generate_visit_pdf (PK: {pk}): {str(e)}\n{error_trace}")
        return Response({"error": str(e), "traceback": error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_visit_report_email(request, pk):
    """
    Endpoint para enviar el reporte por correo electrónico.
    """
    try:
        report = get_object_or_404(VisitReport, pk=pk)
        recipients = request.data.get('recipients', [])
        
        # Limpiar, normalizar y separar destinatarios por coma o punto y coma
        if isinstance(recipients, str):
            recipients = [recipients]
        
        parsed_recipients = []
        for r in recipients:
            if not r:
                continue
            for email in r.replace(';', ',').split(','):
                email_clean = email.strip()
                if email_clean and email_clean not in parsed_recipients:
                    parsed_recipients.append(email_clean)
        recipients = parsed_recipients
        
        if not recipients:
            if report.client_email:
                for email in report.client_email.replace(';', ',').split(','):
                    email_clean = email.strip()
                    if email_clean and email_clean not in recipients:
                        recipients.append(email_clean)
            else:
                # Si no está en el reporte, intentar obtenerlo en tiempo real de SAP (tabla OSLP)
                try:
                    from apps.sap_integration.sap_query_service import SAPQueryService
                    sap_service = SAPQueryService()
                    if report.client_rut:
                        cust_details = sap_service.get_customer_full_details(report.client_rut)
                        # NUNCA enviar al correo del cliente. Solo al del vendedor (OSLP)
                        salesperson_email = cust_details.get('salesperson_email') if cust_details else None
                        if salesperson_email:
                            for email in salesperson_email.replace(';', ',').split(','):
                                email_clean = email.strip()
                                if email_clean and email_clean not in recipients:
                                    recipients.append(email_clean)
                except Exception as ex:
                    logger.warning(f"Error recuperando correo del vendedor desde SAP en tiempo real: {ex}")
        
        # Si sigue vacío, lanzar un error explicativo
        if not recipients:
            return Response(
                {"error": "Debe proporcionar al menos un correo electrónico de destino (o configurar el vendedor en SAP con su correo)."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        from apps.documents.services.email_service import EmailService
        success, message = EmailService.send_visit_report(report, recipients)
        
        if success:
            from .models import VisitStatus
            report.status = VisitStatus.CLOSED
            report.save()  # Dispara la lógica de cierre en SAP
            return Response({"message": message})
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error en send_visit_report_email: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
