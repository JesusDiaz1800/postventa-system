from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VisitReport, DocumentAttachment
from .services.professional_pdf_generator import ProfessionalPDFGenerator
from django.core.files.base import ContentFile
import io
import logging
from .serializers import VisitReportSerializer

logger = logging.getLogger(__name__)

@receiver(post_save, sender=VisitReport)
def generate_visit_report_pdf(sender, instance, created, **kwargs):
    """
    Genera automáticamente el PDF cuando se crea un reporte de visita.
    """
    if created and not instance.pdf_file:
        logger.info(f"Iniciando generación de PDF para reporte {instance.report_number}")
        try:
            # Serializar datos del reporte
            serializer = VisitReportSerializer(instance)
            report_data = serializer.data
            
            # Generar PDF
            generator = ProfessionalPDFGenerator()
            pdf_buffer = io.BytesIO()
            
            # El método acepta un path o un buffer file-like
            success = generator.generate_visit_report_pdf(report_data, pdf_buffer)
            
            if success:
                # Guardar el archivo PDF en el reporte
                filename = f"reporte_visita_{instance.report_number}.pdf"
                instance.pdf_file.save(filename, ContentFile(pdf_buffer.getvalue()), save=False)
                instance.save(update_fields=['pdf_file'])
                logger.info(f"PDF generado y guardado exitosamente para reporte {instance.report_number}")
            else:
                logger.error(f"Fallo en la generación del PDF (método retornó False) para reporte {instance.report_number}")
            
        except Exception as e:
            logger.error(f"Error generardo PDF para reporte {instance.report_number}: {str(e)}", exc_info=True)
