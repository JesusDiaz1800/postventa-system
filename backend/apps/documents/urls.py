from django.urls import path
from .views import report_attachments

urlpatterns = [
    # Adjuntos de reportes (Visita, Laboratorio, Proveedor)
    path('report-attachments/<int:report_id>/<str:report_type>/', report_attachments.list_report_attachments, name='list-report-attachments'),
    path('report-attachments/<int:report_id>/<str:report_type>/upload/', report_attachments.upload_report_attachment, name='upload-report-attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/download/', report_attachments.download_report_attachment, name='download-report-attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/view/', report_attachments.view_report_attachment, name='view-report-attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/delete/', report_attachments.delete_report_attachment, name='delete-report-attachment'),
]
