from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Notification, NotificationCategory, NotificationPreferences


def setup_notification_permissions():
    """Configurar permisos del sistema de notificaciones"""
    
    # Crear grupos si no existen
    groups = {
        'notification_admins': 'Administradores de notificaciones',
        'notification_managers': 'Gestores de notificaciones',
        'notification_viewers': 'Visualizadores de notificaciones'
    }
    
    for group_name, description in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
    
    # Obtener content types
    notification_ct = ContentType.objects.get_for_model(Notification)
    category_ct = ContentType.objects.get_for_model(NotificationCategory)
    preferences_ct = ContentType.objects.get_for_model(NotificationPreferences)
    
    # Definir permisos por grupo
    group_permissions = {
        'notification_admins': {
            notification_ct: ['add', 'change', 'delete', 'view'],
            category_ct: ['add', 'change', 'delete', 'view'],
            preferences_ct: ['add', 'change', 'delete', 'view']
        },
        'notification_managers': {
            notification_ct: ['add', 'change', 'view'],
            category_ct: ['change', 'view'],
            preferences_ct: ['change', 'view']
        },
        'notification_viewers': {
            notification_ct: ['view'],
            category_ct: ['view'],
            preferences_ct: ['view']
        }
    }
    
    # Crear permisos especiales
    special_permissions = [
        ('can_broadcast', 'Can broadcast system notifications'),
        ('can_manage_preferences', 'Can manage notification preferences'),
        ('can_view_system_metrics', 'Can view notification system metrics')
    ]
    
    for codename, name in special_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=notification_ct
        )
    
    # Asignar permisos especiales
    admin_group = Group.objects.get(name='notification_admins')
    manager_group = Group.objects.get(name='notification_managers')
    
    admin_group.permissions.add(
        Permission.objects.get(codename='can_broadcast'),
        Permission.objects.get(codename='can_manage_preferences'),
        Permission.objects.get(codename='can_view_system_metrics')
    )
    
    manager_group.permissions.add(
        Permission.objects.get(codename='can_broadcast')
    )
    
    # Asignar permisos CRUD
    for group_name, content_types in group_permissions.items():
        group = Group.objects.get(name=group_name)
        
        for content_type, actions in content_types.items():
            for action in actions:
                codename = f'{action}_{content_type.model}'
                try:
                    perm = Permission.objects.get(
                        codename=codename,
                        content_type=content_type
                    )
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    print(f'Permiso no encontrado: {codename}')


def check_notification_permission(user, notification_type):
    """
    Verificar si un usuario tiene permiso para recibir un tipo de notificación.
    """
    if user.is_superuser:
        return True
        
    # Verificar grupos
    if notification_type == 'system_alert':
        return user.groups.filter(name__in=[
            'notification_admins',
            'notification_managers'
        ]).exists()
    
    if notification_type == 'workflow_approval_required':
        return user.groups.filter(name__in=[
            'document_reviewers',
            'managers',
            'supervisors'
        ]).exists()
    
    # Verificar permisos específicos
    if notification_type.startswith('document_'):
        return user.has_perm('documents.view_document')
    
    if notification_type.startswith('incident_'):
        return user.has_perm('incidents.view_incident')
    
    if notification_type.startswith('quality_report_'):
        return user.has_perm('quality.view_report')
    
    if notification_type.startswith('visit_report_'):
        return user.has_perm('visits.view_report')
    
    return True


def get_user_notification_permissions(user):
    """
    Obtener todos los permisos de notificación de un usuario.
    """
    permissions = {
        'can_broadcast': user.has_perm('notifications.can_broadcast'),
        'can_manage_preferences': user.has_perm('notifications.can_manage_preferences'),
        'can_view_metrics': user.has_perm('notifications.can_view_system_metrics'),
        'is_admin': user.groups.filter(name='notification_admins').exists(),
        'is_manager': user.groups.filter(name='notification_managers').exists(),
        'allowed_categories': [],
        'allowed_types': []
    }
    
    # Obtener categorías permitidas
    if user.is_superuser:
        permissions['allowed_categories'] = NotificationCategory.objects.values_list(
            'name', flat=True
        )
    else:
        # Filtrar por permisos
        category_filters = Q()
        
        if user.has_perm('documents.view_document'):
            category_filters |= Q(name='documents')
        
        if user.has_perm('incidents.view_incident'):
            category_filters |= Q(name='incidents')
        
        if user.has_perm('quality.view_report'):
            category_filters |= Q(name='reports')
        
        if user.groups.filter(name__in=['managers', 'supervisors']).exists():
            category_filters |= Q(name__in=['system', 'deadlines'])
        
        permissions['allowed_categories'] = NotificationCategory.objects.filter(
            category_filters
        ).values_list('name', flat=True)
    
    # Obtener tipos permitidos
    from .config import NOTIFICATION_TYPES
    permissions['allowed_types'] = [
        notification_type
        for notification_type in NOTIFICATION_TYPES.keys()
        if check_notification_permission(user, notification_type)
    ]
    
    return permissions