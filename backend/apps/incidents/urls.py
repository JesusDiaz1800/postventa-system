from django.urls import path
from . import views, attachment_views, views_escalation

urlpatterns = [
    # Main incident views
    path('', views.IncidentListCreateView.as_view(), name='incident-list-create'),
    path('<int:pk>/', views.IncidentRetrieveUpdateDestroyView.as_view(), name='incident-detail'),

    # Status and actions
    path('<int:incident_id>/status/', views.update_incident_status, name='incident-update-status'),
    path('<int:incident_id>/close/', views.close_incident, name='incident-close'),
    path('<int:incident_id>/reopen/', views.reopen_incident, name='incident-reopen'),


    # Image handling
    path('<int:incident_id>/images/', views.upload_incident_image, name='incident-upload-image'),
    path('<int:incident_id>/images/list/', views.list_incident_images, name='incident-list-images'),
    path('<int:incident_id>/images/<int:image_id>/', views.view_incident_image, name='incident-view-image'),
    path('images/<int:image_id>/analyze/', views.analyze_image, name='incident-analyze-image'),

    # Lab reports
    path('<int:incident_id>/lab-reports/', views.create_lab_report, name='incident-create-lab-report'),
    
    # Dashboard
    path('dashboard/', views.incident_dashboard, name='incident-dashboard'),

    # Attachment views from attachment_views.py
    path('<int:incident_id>/attachments/', attachment_views.list_incident_attachments, name='list-incident-attachments'),
    path('<int:incident_id>/attachments/upload/', attachment_views.upload_incident_attachment, name='upload-incident-attachment'),
    path('<int:incident_id>/attachments/<int:attachment_id>/', attachment_views.get_incident_attachment_info, name='get-incident-attachment'),
    path('<int:incident_id>/attachments/<int:attachment_id>/delete/', attachment_views.delete_incident_attachment, name='delete-incident-attachment'),
    path('<int:incident_id>/attachments/<int:attachment_id>/download/', attachment_views.download_incident_attachment, name='download-attachment'),

    # Escalation views from views_escalation.py
    path('<int:incident_id>/escalate/quality/', views_escalation.escalate_to_quality, name='escalate-to-quality'),
    path('escalated/', views_escalation.escalated_incidents, name='escalated-incidents'),
    path('<int:incident_id>/escalate/supplier/', views.escalate_to_supplier, name='escalate-to-supplier'),
    path('<int:incident_id>/fix-escalation/', views.fix_escalation, name='fix-escalation'),
    
]
