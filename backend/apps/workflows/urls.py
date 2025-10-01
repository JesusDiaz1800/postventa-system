from django.urls import path
from . import views

urlpatterns = [
    # Workflows
    path('', views.WorkflowListCreateView.as_view(), name='workflow_list_create'),
    path('<int:pk>/', views.WorkflowRetrieveUpdateDestroyView.as_view(), name='workflow_detail'),
    
    # Workflow states
    path('<int:workflow_id>/states/', views.WorkflowStateListCreateView.as_view(), name='workflow_state_list_create'),
    path('<int:workflow_id>/states/<int:pk>/', views.WorkflowStateRetrieveUpdateDestroyView.as_view(), name='workflow_state_detail'),
    
    # Workflow transitions
    path('<int:workflow_id>/transitions/', views.WorkflowTransitionListCreateView.as_view(), name='workflow_transition_list_create'),
    path('<int:workflow_id>/transitions/<int:pk>/', views.WorkflowTransitionRetrieveUpdateDestroyView.as_view(), name='workflow_transition_detail'),
    
    # Incident workflow actions
    path('incidents/<int:incident_id>/apply/', views.apply_workflow_to_incident, name='apply_workflow_to_incident'),
    path('incidents/<int:incident_id>/transition/', views.transition_incident_workflow, name='transition_incident_workflow'),
    path('incidents/<int:incident_id>/status/', views.incident_workflow_status, name='incident_workflow_status'),
    
    # Dashboard
    path('dashboard/', views.workflow_dashboard, name='workflow_dashboard'),
]
