from django.urls import path
from . import views
from . import download_views
from . import test_views
from . import test_visit_view
from . import file_views
from . import pdf_views
from . import views_traceability
from . import document_views
from . import attachment_views
from . import views_upload
from . import views_quality
from . import views_documents
from . import views_pdf_generation
from . import views_pdf
from . import test_visit_simple
from . import incident_attachment_views
from . import report_attachment_views
from . import supplier_attachment_views

urlpatterns = [
    path('quality-reports/internal/', views_quality.internal_quality_reports, name='internal_quality_reports'),
    # ==================== GESTIÓN MEJORADA DE DOCUMENTOS ====================
    
    # Información de documentos
    path('info/<str:document_type>/<int:incident_id>/<int:document_id>/', views_documents.get_document_info, name='get_document_info'),
    path('open/<str:document_type>/<int:incident_id>/<str:filename>/', views_documents.open_document_direct, name='open_document_direct'),
    path('incident/<int:incident_id>/documents/', views_documents.list_incident_documents, name='list_incident_documents'),
    
    # ==================== GENERACIÓN DE PDFs PROFESIONALES ====================
    
    # Generación de PDFs
    path('generate-pdf/visit-report/<int:report_id>/', views_pdf_generation.generate_visit_report_pdf, name='generate_visit_report_pdf'),
    path('generate-pdf/lab-report/<int:report_id>/', views_pdf_generation.generate_lab_report_pdf, name='generate_lab_report_pdf'),
    path('generate-pdf/supplier-report/<int:report_id>/', views_pdf_generation.generate_supplier_report_pdf, name='generate_supplier_report_pdf'),
    
    # Nuevos endpoints para generación de PDFs desde formularios
    path('pdf/visit-report/', views_pdf.generate_visit_report_pdf, name='generate_visit_report_pdf_form'),
    path('pdf/lab-report-client/', views_pdf.generate_lab_report_client_pdf, name='generate_lab_report_client_pdf_form'),
    path('pdf/lab-report-internal/', views_pdf.generate_lab_report_internal_pdf, name='generate_lab_report_internal_pdf_form'),
    path('pdf/supplier-report/', views_pdf.generate_supplier_report_pdf, name='generate_supplier_report_pdf_form'),
    path('pdf/quality-report/', views_pdf.generate_quality_report_pdf, name='generate_quality_report_pdf_form'),
    
    # Generación de número de orden
    path('generate-order-number/', views.generate_order_number, name='generate_order_number'),
    path('incident/<int:incident_id>/documents-status/', views_pdf.get_incident_documents_status, name='get_incident_documents_status'),
    
    # ==================== ADJUNTOS DE INCIDENCIAS ====================
    
    # Adjuntos de incidencias
    path('incident-attachments/<int:incident_id>/', incident_attachment_views.list_incident_attachments, name='list_incident_attachments'),
    path('incident-attachments/<int:incident_id>/upload/', incident_attachment_views.upload_incident_attachment, name='upload_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/download/', incident_attachment_views.download_incident_attachment, name='download_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/view/', incident_attachment_views.view_incident_attachment, name='view_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/delete/', incident_attachment_views.delete_incident_attachment, name='delete_incident_attachment'),
    path('incident-attachments/<int:incident_id>/<int:attachment_id>/info/', incident_attachment_views.get_incident_attachment_info, name='get_incident_attachment_info'),
    
    # ==================== ADJUNTOS DE REPORTES ====================
    
    # Adjuntos de reportes
    path('report-attachments/<int:report_id>/<str:report_type>/', report_attachment_views.list_report_attachments, name='list_report_attachments'),
    path('report-attachments/<int:report_id>/<str:report_type>/upload/', report_attachment_views.upload_report_attachment, name='upload_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/download/', report_attachment_views.download_report_attachment, name='download_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/view/', report_attachment_views.view_report_attachment, name='view_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/delete/', report_attachment_views.delete_report_attachment, name='delete_report_attachment'),
    path('report-attachments/<int:report_id>/<str:report_type>/<int:attachment_id>/info/', report_attachment_views.get_report_attachment_info, name='get_report_attachment_info'),
    
    # ==================== ADJUNTOS DE REPORTES DE PROVEEDORES ====================
    
    # Adjuntos específicos de reportes de proveedores
    path('supplier-reports/<int:report_id>/attachments/', supplier_attachment_views.list_supplier_report_attachments, name='list_supplier_report_attachments'),
    path('supplier-reports/upload/', supplier_attachment_views.upload_supplier_report_attachment, name='upload_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/download/', supplier_attachment_views.download_supplier_report_attachment, name='download_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/view/', supplier_attachment_views.view_supplier_report_attachment, name='view_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/delete/', supplier_attachment_views.delete_supplier_report_attachment, name='delete_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/info/', supplier_attachment_views.get_supplier_report_attachment_info, name='get_supplier_report_attachment_info'),
    
]
