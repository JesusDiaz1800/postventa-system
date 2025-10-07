from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowTemplateViewSet,
    WorkflowStepViewSet,
    WorkflowInstanceViewSet,
    WorkflowApprovalViewSet,
    WorkflowHistoryViewSet,
    WorkflowRuleViewSet,
    WorkflowStatsViewSet,
    WorkflowSearchViewSet
)

router = DefaultRouter()
router.register(r'templates', WorkflowTemplateViewSet, basename='workflow-template')
router.register(r'steps', WorkflowStepViewSet, basename='workflow-step')
router.register(r'instances', WorkflowInstanceViewSet, basename='workflow-instance')
router.register(r'approvals', WorkflowApprovalViewSet, basename='workflow-approval')
router.register(r'history', WorkflowHistoryViewSet, basename='workflow-history')
router.register(r'rules', WorkflowRuleViewSet, basename='workflow-rule')
router.register(r'stats', WorkflowStatsViewSet, basename='workflow-stats')
router.register(r'search', WorkflowSearchViewSet, basename='workflow-search')

urlpatterns = [
    path('', include(router.urls)),
]