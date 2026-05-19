"""
User management URLs
"""

from django.urls import path
from . import views, debug_views, views_security

urlpatterns = [
    # Authentication endpoints
    path('login/', views.login_view, name='login'),
    path('download-ca/', views_security.download_ca_cert, name='download_ca_cert'),
    path('test-connectivity/', debug_views.test_connectivity, name='test_connectivity'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('me/', views.user_profile, name='user_me'),
    path('debug-auth/', views.debug_auth, name='debug_auth'),
    path('debug-create-user/', views.debug_create_user, name='debug_create_user'),
    path('permissions/', views.user_permissions, name='user_permissions'),
    path('permissions/roles/', views.RolePermissionListView.as_view(), name='role_permission_list'),
    path('permissions/roles/<str:role>/', views.RolePermissionDetailView.as_view(), name='role_permission_detail'),
    path('change-password/', views.change_own_password, name='change_own_password'),
    
    # User CRUD operations
    path('', views.UserListCreateView.as_view(), name='user_list_create'),
    path('<int:pk>/', views.UserRetrieveUpdateDestroyView.as_view(), name='user_detail'),
    
    # User management actions
    path('stats/', views.user_stats, name='user_stats'),
    path('<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
]