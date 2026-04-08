from django.urls import path
from .views import main as views
from .views import download
from .views import file
from .views import traceability as views_traceability
from .views import document_generation as document_views
from .views import attachments_legacy as attachment_views
from .views import upload as views_upload
from .views import quality as views_quality
from .views import documents as views_documents
from .views import incident_attachments as incident_attachment_views
from .views import report_attachments as report_attachment_views
from .views import supplier_attachments as supplier_attachment_views
from .views import attachment as views_attachment

urlpatterns = [
    # ==================== REPORTES DE CALIDAD ====================
    path('quality-reports/internal/', views_quality.internal_quality_reports, name='internal_quality_reports'),
    
    # ==================== GESTIÓN DE DOCUMENTOS ====================
    
    # Información de documentos
    path('info/<str:document_type>/<int:incident_id>/<int:document_id>/', views_documents.get_document_info, name='get_document_info'),
    path('open/<str:document_type>/<int:incident_id>/<str:filename>', views_documents.open_document_direct, name='open_document_direct'),
    path('incident/<int:incident_id>/documents/', views_documents.list_incident_documents, name='list_incident_documents'),
    
    # Generación de número de orden
    path('generate-order-number/', views.generate_order_number, name='generate_order_number'),
    
    # ==================== ADJUNTOS DE INCIDENCIAS ====================
    
    path('incident-attachments/<int:incident_id>/', incident_attachment_views.IncidentAttachmentListCreateView.as_view(), name='list_incident_attachments'),
    path('incident-attachments/<int:incident_id>/upload/', incident_attachment_views.IncidentAttachmentListCreateView.as_view(), name='upload_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/download/', incident_attachment_views.download_incident_attachment, name='download_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/view/', incident_attachment_views.view_incident_attachment, name='view_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/delete/', incident_attachment_views.IncidentAttachmentDetailView.as_view(), name='delete_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/info/', incident_attachment_views.IncidentAttachmentDetailView.as_view(), name='get_incident_attachment_info'),
    
    # ==================== ADJUNTOS DE REPORTES ====================
    
    path('report-attachments/<int:report_id>/<str:report_type>/', report_attachment_views.list_report_attachments, name='list_report_attachments'),
    path('report-attachments/<int:report_id>/<str:report_type>/upload/', report_attachment_views.upload_report_attachment, name='upload_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/download/', report_attachment_views.download_report_attachment, name='download_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/view/', report_attachment_views.view_report_attachment, name='view_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/delete/', report_attachment_views.delete_report_attachment, name='delete_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/info/', report_attachment_views.get_report_attachment_info, name='get_report_attachment_info'),
    
    # ==================== ADJUNTOS DE PROVEEDORES ====================
    
    path('supplier-reports/<int:report_id>/attachments/', supplier_attachment_views.list_supplier_report_attachments, name='list_supplier_report_attachments'),
    path('supplier-reports/upload/', supplier_attachment_views.upload_supplier_report_attachment, name='upload_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/download/', supplier_attachment_views.download_supplier_report_attachment, name='download_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/view/', supplier_attachment_views.view_supplier_report_attachment, name='view_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/delete/', supplier_attachment_views.delete_supplier_report_attachment, name='delete_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/info/', supplier_attachment_views.get_supplier_report_attachment_info, name='get_supplier_report_attachment_info'),

    # ==================== TRAZABILIDAD Y REPORTES (Vistas basadas en clases) ====================
    path('visit-reports/', views_traceability.VisitReportListCreateView.as_view(), name='visit-report-list'),
    path('visit-reports/<int:pk>/', views_traceability.VisitReportRetrieveUpdateDestroyView.as_view(), name='visit-report-detail'),
    path('visit-reports/<int:pk>/download/', views_traceability.download_visit_report, name='visit-report-download'),
    
    path('lab-reports/', views_traceability.LabReportListCreateView.as_view(), name='lab-report-list'),
    path('lab-reports/<int:pk>/', views_traceability.LabReportRetrieveUpdateDestroyView.as_view(), name='lab-report-detail'),
    
    path('supplier-reports/', views_traceability.SupplierReportListCreateView.as_view(), name='supplier-report-list'),
    path('supplier-reports/<int:pk>/', views_traceability.SupplierReportRetrieveUpdateDestroyView.as_view(), name='supplier-report-detail'),
    path('supplier-reports/<int:pk>/generate/', views_traceability.generate_supplier_report_document, name='supplier-report-generate'),
    path('supplier-reports/<int:pk>/download/', views_traceability.download_supplier_report, name='supplier-report-download'),
    path('upload/supplier-report/', views_traceability.upload_supplier_report_document, name='upload-supplier-report'),
    
    path('workflow/<int:incident_id>/', views_traceability.incident_workflow, name='incident-workflow'),
    path('available-incidents/', views_traceability.available_incidents, name='available-incidents'),
    path('statistics/', views_traceability.document_statistics, name='document-statistics'),
    path('dashboard/', views_traceability.document_statistics, name='document-dashboard'),
    
    path('supplier-reports/<int:pk>/send-email/', views_traceability.send_supplier_report_email, name='supplier-report-send-email'),
    
    # ==================== REPORTES DE CALIDAD (CRUD) ====================
    path('quality-reports/', views_quality.QualityReportListCreateView.as_view(), name='quality-report-list'),
    path('quality-reports/<int:pk>/', views_quality.QualityReportRetrieveUpdateDestroyView.as_view(), name='quality-report-detail'),
    path('quality-reports/<int:report_id>/generate/', views_quality.generate_quality_report_document, name='quality-report-generate'),
    path('quality-reports/summary/', views_quality.quality_reports_summary, name='quality-report-summary'),
    path('quality-reports/by-incident/<int:incident_id>/', views_quality.quality_reports_by_incident, name='quality-reports-by-incident'),
    path('quality-reports/<int:pk>/escalate-supplier/', views_quality.escalate_to_supplier, name='quality-report-escalate-supplier'),
    path('quality-reports/<int:pk>/send-email/', views_quality.send_quality_report_email, name='quality-report-send-email'),
    path('quality-reports/<int:pk>/download/', views_quality.download_quality_report, name='quality-report-download'),
    path('upload/quality-report/', views_quality.upload_quality_report_document, name='upload-quality-report'),
    
    # ==================== GENERAL ATTACHMENTS ====================
    path('upload-attachment/', views_attachment.upload_attachment, name='upload-attachment'),
    path('attachments/incident/<int:incident_id>/', views_attachment.list_attachments_by_incident, name='list-attachments-by-incident'),
    path('attachments/v2/incident/<int:incident_id>/', views_attachment.list_attachments_by_incident, name='list-attachments-by-incident-v2'),
    path('attachments/incident/<int:incident_id>/upload/', views_attachment.upload_attachment, name='upload-attachment-by-incident'),
    path('attachments/incident/<int:incident_id>/<int:attachment_id>/download/', views_attachment.download_attachment, name='download-attachment'),
    path('attachments/incident/<int:incident_id>/<int:attachment_id>/view/', views_attachment.view_attachment, name='view-attachment'),
    path('attachments/incident/<int:incident_id>/<int:attachment_id>/delete/', views_attachment.delete_attachment, name='delete-attachment'),
]

