from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Workflow, WorkflowState, WorkflowTransition, IncidentWorkflow, WorkflowHistory
from .serializers import (
    WorkflowSerializer, WorkflowCreateUpdateSerializer,
    WorkflowStateSerializer, WorkflowStateCreateUpdateSerializer,
    WorkflowTransitionSerializer, WorkflowTransitionCreateUpdateSerializer,
    IncidentWorkflowSerializer, WorkflowHistorySerializer,
    WorkflowTransitionRequestSerializer
)


class WorkflowListCreateView(generics.ListCreateAPIView):
    """List and create workflows"""
    queryset = Workflow.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkflowCreateUpdateSerializer
        return WorkflowSerializer


class WorkflowRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete workflows"""
    queryset = Workflow.objects.all()
    serializer_class = WorkflowCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkflowStateListCreateView(generics.ListCreateAPIView):
    """List and create workflow states"""
    serializer_class = WorkflowStateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return WorkflowState.objects.filter(workflow_id=workflow_id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkflowStateCreateUpdateSerializer
        return WorkflowStateSerializer
    
    def perform_create(self, serializer):
        workflow = get_object_or_404(Workflow, id=self.kwargs['workflow_id'])
        serializer.save(workflow=workflow)


class WorkflowStateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete workflow states"""
    serializer_class = WorkflowStateCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return WorkflowState.objects.filter(workflow_id=workflow_id)


class WorkflowTransitionListCreateView(generics.ListCreateAPIView):
    """List and create workflow transitions"""
    serializer_class = WorkflowTransitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return WorkflowTransition.objects.filter(workflow_id=workflow_id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkflowTransitionCreateUpdateSerializer
        return WorkflowTransitionSerializer
    
    def perform_create(self, serializer):
        workflow = get_object_or_404(Workflow, id=self.kwargs['workflow_id'])
        serializer.save(workflow=workflow)


class WorkflowTransitionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete workflow transitions"""
    serializer_class = WorkflowTransitionCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return WorkflowTransition.objects.filter(workflow_id=workflow_id)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_workflow_to_incident(request, incident_id):
    """Apply a workflow to an incident"""
    from apps.incidents.models import Incident
    
    incident = get_object_or_404(Incident, id=incident_id)
    workflow_id = request.data.get('workflow_id')
    
    if not workflow_id:
        return Response(
            {'error': 'workflow_id es requerido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    workflow = get_object_or_404(Workflow, id=workflow_id, is_active=True)
    
    # Check if incident already has a workflow
    if hasattr(incident, 'workflow_progress'):
        return Response(
            {'error': 'La incidencia ya tiene un workflow asignado'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get initial state
    initial_state = workflow.states.filter(is_initial=True).first()
    if not initial_state:
        return Response(
            {'error': 'El workflow no tiene un estado inicial definido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create incident workflow
    incident_workflow = IncidentWorkflow.objects.create(
        incident=incident,
        workflow=workflow,
        current_state=initial_state
    )
    
    # Create history entry
    WorkflowHistory.objects.create(
        incident_workflow=incident_workflow,
        to_state=initial_state,
        user=request.user,
        description=f'Workflow {workflow.name} aplicado a la incidencia'
    )
    
    # Update incident status
    incident.estado = initial_state.name
    incident.save()
    
    return Response({
        'message': 'Workflow aplicado exitosamente',
        'workflow': IncidentWorkflowSerializer(incident_workflow).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def transition_incident_workflow(request, incident_id):
    """Transition incident workflow to next state"""
    from apps.incidents.models import Incident
    
    incident = get_object_or_404(Incident, id=incident_id)
    
    if not hasattr(incident, 'workflow_progress'):
        return Response(
            {'error': 'La incidencia no tiene un workflow asignado'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    incident_workflow = incident.workflow_progress
    serializer = WorkflowTransitionRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    to_state_id = serializer.validated_data['to_state_id']
    to_state = get_object_or_404(WorkflowState, id=to_state_id)
    
    # Check if transition is valid
    transition = WorkflowTransition.objects.filter(
        workflow=incident_workflow.workflow,
        from_state=incident_workflow.current_state,
        to_state=to_state,
        is_active=True
    ).first()
    
    if not transition:
        return Response(
            {'error': 'Transición no válida'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user has permission to make this transition
    user_role = request.user.role
    if transition.allowed_roles and user_role not in transition.allowed_roles:
        return Response(
            {'error': 'No tiene permisos para realizar esta transición'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check required conditions
    # TODO: Implement condition checking logic
    
    # Perform transition
    from_state = incident_workflow.current_state
    incident_workflow.current_state = to_state
    incident_workflow.save()
    
    # Create history entry
    WorkflowHistory.objects.create(
        incident_workflow=incident_workflow,
        from_state=from_state,
        to_state=to_state,
        transition=transition,
        user=request.user,
        description=serializer.validated_data['description'],
        metadata=serializer.validated_data['metadata']
    )
    
    # Update incident status
    incident.estado = to_state.name
    incident.save()
    
    return Response({
        'message': 'Transición realizada exitosamente',
        'workflow': IncidentWorkflowSerializer(incident_workflow).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def incident_workflow_status(request, incident_id):
    """Get incident workflow status"""
    from apps.incidents.models import Incident
    
    incident = get_object_or_404(Incident, id=incident_id)
    
    if not hasattr(incident, 'workflow_progress'):
        return Response({
            'has_workflow': False,
            'message': 'La incidencia no tiene un workflow asignado'
        })
    
    incident_workflow = incident.workflow_progress
    
    # Get available transitions
    available_transitions = WorkflowTransition.objects.filter(
        workflow=incident_workflow.workflow,
        from_state=incident_workflow.current_state,
        is_active=True
    )
    
    # Filter by user role
    user_role = request.user.role
    available_transitions = available_transitions.filter(
        models.Q(allowed_roles__isnull=True) | 
        models.Q(allowed_roles__contains=[user_role])
    )
    
    # Get workflow history
    history = incident_workflow.history.all().order_by('-created_at')[:10]
    
    return Response({
        'has_workflow': True,
        'workflow': IncidentWorkflowSerializer(incident_workflow).data,
        'available_transitions': WorkflowTransitionSerializer(available_transitions, many=True).data,
        'history': WorkflowHistorySerializer(history, many=True).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def workflow_dashboard(request):
    """Get workflow dashboard data"""
    # Get workflow statistics
    total_workflows = Workflow.objects.filter(is_active=True).count()
    total_incidents_with_workflow = IncidentWorkflow.objects.count()
    
    # Get workflows by incident type
    workflows_by_type = Workflow.objects.filter(is_active=True).values('incident_type').annotate(
        count=models.Count('id')
    )
    
    # Get recent workflow activities
    recent_activities = WorkflowHistory.objects.all().order_by('-created_at')[:20]
    
    return Response({
        'kpis': {
            'total_workflows': total_workflows,
            'total_incidents_with_workflow': total_incidents_with_workflow,
        },
        'workflows_by_type': list(workflows_by_type),
        'recent_activities': WorkflowHistorySerializer(recent_activities, many=True).data
    })
