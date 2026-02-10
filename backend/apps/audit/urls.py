from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet
from .views_restore import DeletedItemViewSet

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='audit-log')
router.register(r'deleted-items', DeletedItemViewSet, basename='deleted-item')

urlpatterns = [
    path('', include(router.urls)),
]