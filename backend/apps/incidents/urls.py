from django.urls import path
from . import views, attachment_views, views_escalation

urlpatterns = [
    # Test endpoints
    path('test/', views.test_incidents_endpoint, name='test_incidents'),
    path('simple/', views.simple_incidents_list, name='simple_incidents_list'),
    path('debug/', views.debug_incidents_list, name='debug_incidents_list'),
    
    # Incident CRUD
    path('', views.IncidentListCreateView.as_view(), name='incident_list_create'),
    path('<int:pk>/', views.IncidentRetrieveUpdateDestroyView.as_view(), name='incident_detail'),
    
    # Incident actions
    path('<int:incident_id>/images/', views.upload_incident_image, name='upload_incident_image'),
    path('<int:incident_id>/images/list/', views.list_incident_images, name='list_incident_images'),
    path('<int:incident_id>/images/<int:image_id>/view/', views.view_incident_image, name='view_incident_image'),
    path('<int:incident_id>/status/', views.update_incident_status, name='update_incident_status'),
    path('<int:incident_id>/lab-reports/', views.create_lab_report, name='create_lab_report'),
    
    # Image analysis
    path('images/<int:image_id>/analyze/', views.analyze_image, name='analyze_image'),
    
    # Dashboard
    path('dashboard/', views.incident_dashboard, name='incident_dashboard'),
    
    # Incident attachments
    path('<int:incident_id>/attachments/upload/', attachment_views.upload_incident_attachment, name='upload_incident_attachment'),
    path('<int:incident_id>/attachments/', attachment_views.list_incident_attachments, name='list_incident_attachments'),
    path('<int:incident_id>/attachments/<int:attachment_id>/download/', attachment_views.download_incident_attachment, name='download_incident_attachment'),
    path('<int:incident_id>/attachments/<int:attachment_id>/view/', attachment_views.view_incident_attachment, name='view_incident_attachment'),
    path('<int:incident_id>/attachments/<int:attachment_id>/delete/', attachment_views.delete_incident_attachment, name='delete_incident_attachment'),
    path('<int:incident_id>/attachments/<int:attachment_id>/info/', attachment_views.get_incident_attachment_info, name='get_incident_attachment_info'),
    
    # Escalation endpoints
    path('<int:incident_id>/escalate/quality/', views_escalation.escalate_to_quality, name='escalate_to_quality'),
    path('<int:incident_id>/escalate/supplier/', views_escalation.escalate_to_supplier, name='escalate_to_supplier'),
    path('<int:incident_id>/close/', views_escalation.close_incident, name='close_incident'),
    path('<int:incident_id>/reopen/', views_escalation.reopen_incident, name='reopen_incident'),
    path('escalated/', views_escalation.get_escalated_incidents, name='get_escalated_incidents'),
]
