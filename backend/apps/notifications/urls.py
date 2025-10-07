from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, 
    NotificationPreferenceViewSet
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preference')

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs específicas para compatibilidad con el cliente
    path('notifications/recent/', NotificationViewSet.as_view({'get': 'recent'}), name='notification-recent'),
    path('notifications/unread_count/', NotificationViewSet.as_view({'get': 'unread_count'}), name='notification-unread-count'),
    path('notifications/important/', NotificationViewSet.as_view({'get': 'important'}), name='notification-important'),
]
