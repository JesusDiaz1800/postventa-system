from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

from .models import (
    WorkflowTemplate, 
    WorkflowStep, 
    WorkflowInstance, 
    WorkflowApproval, 
    WorkflowHistory,
    WorkflowRule
)
from .serializers import (
    WorkflowTemplateSerializer,
    WorkflowStepSerializer,
    WorkflowInstanceSerializer,
    WorkflowInstanceCreateSerializer,
    WorkflowApprovalSerializer,
    WorkflowApprovalActionSerializer,
    WorkflowHistorySerializer,
    WorkflowRuleSerializer,
    WorkflowStatsSerializer,
    WorkflowDashboardSerializer,
    WorkflowSearchSerializer
)
from .services import WorkflowService


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet para plantillas de workflow"""
    serializer_class = WorkflowTemplateSerializer
    permission_classes = [IsAuthenticated]
    queryset = WorkflowTemplate.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Obtener plantillas por tipo"""
        workflow_type = request.query_params.get('type')
        if workflow_type:
            templates = self.get_queryset().filter(workflow_type=workflow_type)
            serializer = self.get_serializer(templates, many=True)
            return Response(serializer.data)
        return Response({'error': 'Tipo de workflow requerido'}, status=400)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Obtener plantilla por defecto"""
        workflow_type = request.query_params.get('type')
        if workflow_type:
            template = self.get_queryset().filter(
                workflow_type=workflow_type,
                is_default=True
            ).first()
            if template:
                serializer = self.get_serializer(template)
                return Response(serializer.data)
            return Response({'error': 'No hay plantilla por defecto'}, status=404)
        return Response({'error': 'Tipo de workflow requerido'}, status=400)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicar plantilla de workflow"""
        template = self.get_object()
        new_template = WorkflowService.duplicate_template(template, request.user)
        serializer = self.get_serializer(new_template)
        return Response(serializer.data)


class WorkflowStepViewSet(viewsets.ModelViewSet):
    """ViewSet para pasos de workflow"""
    serializer_class = WorkflowStepSerializer
    permission_classes = [IsAuthenticated]
    queryset = WorkflowStep.objects.all()
    
    def get_queryset(self):
        """Filtrar pasos por plantilla"""
        queryset = super().get_queryset()
        template_id = self.request.query_params.get('template')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        return queryset


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet para instancias de workflow"""
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener instancias del usuario"""
        user = self.request.user
        return WorkflowInstance.objects.filter(
            Q(started_by=user) | 
            Q(approvals__approver=user) |
            Q(related_incident__assigned_to=user) |
            Q(related_document__created_by=user)
        ).distinct()
    
    def get_serializer_class(self):
        """Usar serializer de creación para POST"""
        if self.action == 'create':
            return WorkflowInstanceCreateSerializer
        return WorkflowInstanceSerializer
    
    @action(detail=False, methods=['get'])
    def my_workflows(self, request):
        """Obtener workflows del usuario actual"""
        workflows = self.get_queryset().filter(started_by=request.user)
        serializer = self.get_serializer(workflows, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Obtener workflows pendientes de aprobación"""
        workflows = self.get_queryset().filter(
            status='in_progress',
            approvals__approver=request.user,
            approvals__status='pending'
        ).distinct()
        serializer = self.get_serializer(workflows, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Obtener workflows vencidos"""
        workflows = self.get_queryset().filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        )
        serializer = self.get_serializer(workflows, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar workflow"""
        instance = self.get_object()
        if instance.status != 'pending':
            return Response(
                {'error': 'Workflow ya iniciado'}, 
                status=400
            )
        
        WorkflowService.start_workflow(instance, request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar workflow"""
        instance = self.get_object()
        if instance.status not in ['pending', 'in_progress']:
            return Response(
                {'error': 'Workflow no puede ser cancelado'}, 
                status=400
            )
        
        WorkflowService.cancel_workflow(instance, request.user, request.data.get('reason', ''))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Obtener progreso del workflow"""
        instance = self.get_object()
        progress_data = WorkflowService.get_workflow_progress(instance)
        return Response(progress_data)
    
    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        """Avanzar workflow al siguiente paso"""
        instance = self.get_object()
        if not instance.can_be_approved_by(request.user):
            return Response(
                {'error': 'No tienes permisos para avanzar este workflow'}, 
                status=403
            )
        
        WorkflowService.advance_workflow(instance, request.user, request.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class WorkflowApprovalViewSet(viewsets.ModelViewSet):
    """ViewSet para aprobaciones de workflow"""
    serializer_class = WorkflowApprovalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener aprobaciones del usuario"""
        return WorkflowApproval.objects.filter(approver=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener aprobaciones pendientes"""
        approvals = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(approvals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Obtener aprobaciones vencidas"""
        approvals = self.get_queryset().filter(
            status='pending',
            due_date__lt=timezone.now()
        )
        serializer = self.get_serializer(approvals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar workflow"""
        approval = self.get_object()
        if approval.status != 'pending':
            return Response(
                {'error': 'Aprobación ya procesada'}, 
                status=400
            )
        
        WorkflowService.approve_workflow(
            approval, 
            request.user, 
            request.data.get('comments', ''),
            request.data.get('metadata', {})
        )
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar workflow"""
        approval = self.get_object()
        if approval.status != 'pending':
            return Response(
                {'error': 'Aprobación ya procesada'}, 
                status=400
            )
        
        WorkflowService.reject_workflow(
            approval, 
            request.user, 
            request.data.get('comments', ''),
            request.data.get('justification', ''),
            request.data.get('metadata', {})
        )
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def delegate(self, request, pk=None):
        """Delegar aprobación"""
        approval = self.get_object()
        if approval.status != 'pending':
            return Response(
                {'error': 'Aprobación ya procesada'}, 
                status=400
            )
        
        delegated_to_id = request.data.get('delegated_to')
        if not delegated_to_id:
            return Response(
                {'error': 'Usuario delegado requerido'}, 
                status=400
            )
        
        WorkflowService.delegate_approval(
            approval, 
            request.user, 
            delegated_to_id,
            request.data.get('comments', '')
        )
        serializer = self.get_serializer(approval)
        return Response(serializer.data)


class WorkflowHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para historial de workflow"""
    serializer_class = WorkflowHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener historial de workflows del usuario"""
        return WorkflowHistory.objects.filter(
            Q(instance__started_by=self.request.user) |
            Q(instance__approvals__approver=self.request.user)
        ).distinct()


class WorkflowRuleViewSet(viewsets.ModelViewSet):
    """ViewSet para reglas de workflow"""
    serializer_class = WorkflowRuleSerializer
    permission_classes = [IsAuthenticated]
    queryset = WorkflowRule.objects.filter(is_active=True)


class WorkflowStatsViewSet(viewsets.ViewSet):
    """ViewSet para estadísticas de workflow"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Obtener datos del dashboard"""
        user = request.user
        
        # Aprobaciones pendientes del usuario
        pending_approvals = WorkflowApproval.objects.filter(
            approver=user,
            status='pending'
        ).order_by('-assigned_at')[:10]
        
        # Workflows activos del usuario
        active_workflows = WorkflowInstance.objects.filter(
            started_by=user,
            status='in_progress'
        ).order_by('-started_at')[:10]
        
        # Workflows recientes
        recent_workflows = WorkflowInstance.objects.filter(
            Q(started_by=user) | Q(approvals__approver=user)
        ).distinct().order_by('-started_at')[:10]
        
        # Workflows vencidos
        overdue_workflows = WorkflowInstance.objects.filter(
            Q(started_by=user) | Q(approvals__approver=user),
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).distinct().order_by('due_date')[:10]
        
        # Próximas fechas límite
        upcoming_deadlines = WorkflowInstance.objects.filter(
            Q(started_by=user) | Q(approvals__approver=user),
            status__in=['pending', 'in_progress'],
            due_date__gt=timezone.now(),
            due_date__lte=timezone.now() + timedelta(days=7)
        ).distinct().order_by('due_date')[:10]
        
        # Estadísticas
        stats = WorkflowService.get_workflow_stats(user)
        
        dashboard_data = {
            'my_pending_approvals': WorkflowApprovalSerializer(pending_approvals, many=True).data,
            'my_active_workflows': WorkflowInstanceSerializer(active_workflows, many=True).data,
            'recent_workflows': WorkflowInstanceSerializer(recent_workflows, many=True).data,
            'overdue_workflows': WorkflowInstanceSerializer(overdue_workflows, many=True).data,
            'upcoming_deadlines': WorkflowInstanceSerializer(upcoming_deadlines, many=True).data,
            'stats': stats
        }
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtener estadísticas generales"""
        user = request.user
        stats = WorkflowService.get_workflow_stats(user)
        return Response(stats)


class WorkflowSearchViewSet(viewsets.ViewSet):
    """ViewSet para búsqueda de workflows"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Buscar workflows"""
        serializer = WorkflowSearchSerializer(data=request.data)
        if serializer.is_valid():
            results = WorkflowService.search_workflows(
                request.user, 
                serializer.validated_data
            )
            return Response(results)
        return Response(serializer.errors, status=400)