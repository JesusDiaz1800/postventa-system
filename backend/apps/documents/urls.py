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
<<<<<<< HEAD
=======
from . import supplier_attachment_views
>>>>>>> 674c244 (tus cambios)

urlpatterns = [
    # Document templates
    path('templates/', views.DocumentTemplateListCreateView.as_view(), name='template_list_create'),
    path('templates/<int:pk>/', views.DocumentTemplateRetrieveUpdateDestroyView.as_view(), name='template_detail'),
    
    # Documents
    path('', views.DocumentListCreateView.as_view(), name='document_list_create'),
    path('by-incidents/', views.documents_by_incidents, name='documents_by_incidents'),
    path('<int:pk>/', views.DocumentRetrieveUpdateDestroyView.as_view(), name='document_detail'),
    
    # Document actions
    path('generate/', views.generate_document, name='generate_document'),
    path('generate/<int:incident_id>/', views.generate_document, name='generate_document_for_incident'),
    path('generate-polifusion-lab-report/', views.generate_polifusion_lab_report, name='generate_polifusion_lab_report'),
    path('generate-polifusion-incident-report/', views.generate_polifusion_incident_report, name='generate_polifusion_incident_report'),
    path('generate-polifusion-visit-report/', views.generate_polifusion_visit_report, name='generate_polifusion_visit_report'),
    
    # Test endpoints (sin autenticación para debug)
    path('test/generate-polifusion-lab-report/', test_views.test_generate_polifusion_lab_report, name='test_generate_polifusion_lab_report'),
    path('test/generate-polifusion-incident-report/', test_views.test_generate_polifusion_incident_report, name='test_generate_polifusion_incident_report'),
    path('test/generate-polifusion-visit-report/', test_visit_view.test_generate_polifusion_visit_report, name='test_generate_polifusion_visit_report'),
    
    # Document download and view
    path('<int:document_id>/download/<str:file_type>/', download_views.download_document, name='download_document'),
    path('<int:document_id>/view/<str:file_type>/', download_views.view_document, name='view_document'),
    path('<int:document_id>/info/', download_views.document_info, name='document_info'),
    
    # Document management
    path('<int:document_id>/edit/', download_views.edit_document, name='edit_document'),
    path('<int:document_id>/delete/', download_views.delete_document, name='delete_document'),
    
    # Search and dashboard
    path('search/', views.search_documents, name='search_documents'),
    path('dashboard/', views.document_dashboard, name='document_dashboard'),
    
    # Real file management
    path('real-files/', file_views.list_real_documents, name='list_real_documents'),
    path('real-files/stats/', file_views.get_folder_stats, name='get_folder_stats'),
    path('real-files/search/', file_views.search_documents, name='search_real_documents'),
    path('real-files/by-type/', file_views.get_documents_by_type, name='get_documents_by_type'),
    path('real-files/<str:filename>/', file_views.get_document_info, name='get_document_info'),
    path('real-files/<str:filename>/serve/', file_views.serve_real_document, name='serve_real_document'),
    path('real-files/<str:filename>/public/', file_views.serve_real_document_public, name='serve_real_document_public'),
    path('real-files/<str:filename>/delete/', file_views.delete_real_document, name='delete_real_document'),
    
    # PDF generation
    path('generate-polifusion-lab-report-pdf/', pdf_views.generate_polifusion_lab_report_pdf, name='generate_polifusion_lab_report_pdf'),
    path('generate-polifusion-incident-report-pdf/', pdf_views.generate_polifusion_incident_report_pdf, name='generate_polifusion_incident_report_pdf'),
    path('generate-polifusion-visit-report-pdf/', pdf_views.generate_polifusion_visit_report_pdf, name='generate_polifusion_visit_report_pdf'),
    path('<int:document_id>/pdf/', pdf_views.serve_pdf_document, name='serve_pdf_document'),
    path('<int:document_id>/pdf/public/', document_views.serve_pdf_public, name='serve_pdf_public'),
    
    # ==================== TRAZABILIDAD DOCUMENTAL ====================
    
    # Reportes de Visita
    path('visit-reports/', views_traceability.VisitReportListCreateView.as_view(), name='visit_report_list_create'),
    path('visit-reports/<int:pk>/', views_traceability.VisitReportRetrieveUpdateDestroyView.as_view(), name='visit_report_detail'),
    path('visit-reports-test/', test_visit_simple.test_visit_reports_simple, name='visit_reports_test'),
    
    # Informes de Laboratorio
    path('lab-reports/', views_traceability.LabReportListCreateView.as_view(), name='lab_report_list_create'),
    path('lab-reports/<int:pk>/', views_traceability.LabReportRetrieveUpdateDestroyView.as_view(), name='lab_report_detail'),
    
    # Informes para Proveedores
    path('supplier-reports/', views_traceability.SupplierReportListCreateView.as_view(), name='supplier_report_list_create'),
    path('supplier-reports/<int:pk>/', views_traceability.SupplierReportRetrieveUpdateDestroyView.as_view(), name='supplier_report_detail'),
    
    # Workflow y Trazabilidad
    path('workflow/<int:incident_id>/', views_traceability.incident_workflow, name='incident_workflow'),
    path('available-incidents/', views_traceability.available_incidents, name='available_incidents'),
    path('statistics/', views_traceability.document_statistics, name='document_statistics'),
    
    # ==================== GENERACIÓN Y GESTIÓN DE DOCUMENTOS ====================
    
    # Generación de documentos
    path('generate/visit-report/<int:report_id>/', document_views.generate_visit_report_document, name='generate_visit_report_document'),
    path('generate/lab-report/<int:report_id>/', document_views.generate_lab_report_document, name='generate_lab_report_document'),
    path('generate/supplier-report/<int:report_id>/', document_views.generate_supplier_report_document, name='generate_supplier_report_document'),
    
    # Gestión de documentos compartidos
    path('shared/', document_views.list_shared_documents, name='list_shared_documents'),
    path('shared/<str:document_type>/<str:filename>/download/', document_views.download_shared_document, name='download_shared_document'),
    path('shared/<str:document_type>/<str:filename>/view/', document_views.view_shared_document, name='view_shared_document'),
    path('shared/<str:document_type>/<str:filename>/delete/', document_views.delete_shared_document, name='delete_shared_document'),
    path('shared/<str:document_type>/<str:filename>/info/', document_views.get_document_info, name='get_document_info'),
    
    # ==================== GESTIÓN DE ARCHIVOS ADJUNTOS ====================
    
    # Archivos adjuntos
    path('attachments/<str:document_type>/<int:document_id>/upload/', attachment_views.upload_attachment, name='upload_attachment'),
    path('attachments/<str:document_type>/<int:document_id>/', attachment_views.list_attachments, name='list_attachments'),
    path('attachments/<str:document_type>/<int:document_id>/<str:filename>/download/', attachment_views.download_attachment, name='download_attachment'),
    path('attachments/<str:document_type>/<int:document_id>/<str:filename>/view/', attachment_views.view_attachment, name='view_attachment'),
    path('attachments/<str:document_type>/<int:document_id>/<str:filename>/delete/', attachment_views.delete_attachment, name='delete_attachment'),
    path('attachments/<str:document_type>/<int:document_id>/<str:filename>/info/', attachment_views.get_attachment_info, name='get_attachment_info'),
    
    # ==================== SUBIDA DE DOCUMENTOS COMPARTIDOS ====================
    
    # Subida de documentos
    path('upload/', views_upload.upload_document, name='upload_document'),
    path('upload/visit-report/', views_upload.upload_visit_report, name='upload_visit_report'),
    path('upload/supplier-report/', views_upload.upload_supplier_report, name='upload_supplier_report'),
    path('upload/lab-report/', views_upload.upload_lab_report, name='upload_lab_report'),
    path('upload/quality-report/', views_upload.upload_quality_report, name='upload_quality_report'),
    path('shared/', views_upload.list_shared_documents, name='list_shared_documents'),
    path('open/<str:document_type>/<int:incident_id>/<str:filename>/', views_upload.open_document, name='open_document'),
    path('search/<str:document_type>/<str:filename>/', views_upload.search_document_by_name, name='search_document_by_name'),
    path('debug/<str:document_type>/<int:incident_id>/', views_upload.debug_shared_folder, name='debug_shared_folder'),
    path('uploaded/<str:document_type>/<int:incident_id>/', views_upload.list_uploaded_documents, name='list_uploaded_documents'),
    path('delete/<str:document_type>/<int:incident_id>/<str:filename>/', views_upload.delete_uploaded_document, name='delete_uploaded_document'),
    path('delete-all/<int:incident_id>/', views_upload.delete_all_incident_documents, name='delete_all_incident_documents'),
    
    # ==================== REPORTES DE CALIDAD ====================
    
    # Reportes de calidad
    path('quality-reports/', views_quality.QualityReportListCreateView.as_view(), name='quality_reports_list_create'),
    path('quality-reports/<int:pk>/', views_quality.QualityReportRetrieveUpdateDestroyView.as_view(), name='quality_reports_detail'),
    path('quality-reports/incident/<int:incident_id>/', views_quality.quality_reports_by_incident, name='quality_reports_by_incident'),
    path('quality-reports/summary/', views_quality.quality_reports_summary, name='quality_reports_summary'),
    path('quality-reports/<int:report_id>/generate/', views_quality.generate_quality_report_document, name='generate_quality_report_document'),
<<<<<<< HEAD
=======
    path('quality-reports/internal/', views_quality.internal_quality_reports, name='internal_quality_reports'),
>>>>>>> 674c244 (tus cambios)
    
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
    
<<<<<<< HEAD
=======
    # ==================== ADJUNTOS DE REPORTES DE PROVEEDORES ====================
    
    # Adjuntos específicos de reportes de proveedores
    path('supplier-reports/<int:report_id>/attachments/', supplier_attachment_views.list_supplier_report_attachments, name='list_supplier_report_attachments'),
    path('supplier-reports/upload/', supplier_attachment_views.upload_supplier_report_attachment, name='upload_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/download/', supplier_attachment_views.download_supplier_report_attachment, name='download_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/view/', supplier_attachment_views.view_supplier_report_attachment, name='view_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/delete/', supplier_attachment_views.delete_supplier_report_attachment, name='delete_supplier_report_attachment'),
    path('supplier-reports/attachments/<int:attachment_id>/info/', supplier_attachment_views.get_supplier_report_attachment_info, name='get_supplier_report_attachment_info'),
    
>>>>>>> 674c244 (tus cambios)
]
