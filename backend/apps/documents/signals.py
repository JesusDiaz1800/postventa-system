from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VisitReport, DocumentAttachment
import logging

logger = logging.getLogger(__name__)

# NOTA: El signal post_save NO dispara sincronización con SAP.
# La sincronización es manejada explícitamente por:
#   - VisitReportListCreateView.perform_create  → sync_report_async
#   - VisitReportRetrieveUpdateDestroyView.perform_update → sync_report_async
#
# Disparar sync desde el signal causaba el bug de PDFs múltiples en SAP:
# cada guardado interno (ej. report.pdf_file.save(...), report.save(update_fields=[...]))
# disparaba un nuevo hilo de sincronización concurrente, resultando en 3-5 syncs
# paralelas del mismo reporte, cada una subiendo y eliminando el PDF en SAP.
