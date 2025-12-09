from rest_framework import permissions


class CanViewIncidents(permissions.BasePermission):
    """
    Permission to view incidents based on user role
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        # All authenticated users can view incidents
        if not user.is_authenticated:
            return False
        
        # Check role-based permissions
<<<<<<< HEAD
        if user.role in ['admin', 'administrador', 'supervisor', 'analyst', 'customer_service', 'management', 'provider']:
=======
        if user.role in ['admin', 'administrador', 'supervisor', 'analyst', 'customer_service', 'management', 'provider', 'technical_service', 'servicio_tecnico', 'tecnico']:
>>>>>>> 674c244 (tus cambios)
            return True
        
        return False


class CanManageIncidents(permissions.BasePermission):
    """
    Permission to manage incidents (create, update, delete) based on user role
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Only certain roles can manage incidents
<<<<<<< HEAD
        if user.role in ['admin', 'administrador', 'supervisor', 'analyst', 'customer_service']:
=======
        if user.role in ['admin', 'administrador', 'supervisor', 'analyst', 'customer_service', 'technical_service', 'servicio_tecnico', 'tecnico']:
>>>>>>> 674c244 (tus cambios)
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admins and supervisors can manage all incidents
        if user.role in ['admin', 'administrador', 'supervisor']:
            return True
        
        # Analysts can manage incidents they created or are assigned to
        if user.role == 'analyst':
            return obj.created_by == user or obj.assigned_to == user
        
        # Customer service can manage all incidents
        if user.role == 'customer_service':
            return True
        
<<<<<<< HEAD
=======
        # Technical service can manage incidents they created or are assigned to
        if user.role in ['technical_service', 'servicio_tecnico', 'tecnico']:
            return obj.created_by == user or obj.assigned_to == user
        
>>>>>>> 674c244 (tus cambios)
        return False


class CanViewLabReports(permissions.BasePermission):
    """
    Permission to view lab reports
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Most roles can view lab reports
        if user.role in ['admin', 'administrador', 'supervisor', 'analyst', 'management']:
            return True
        
        return False


class CanCreateLabReports(permissions.BasePermission):
    """
    Permission to create lab reports
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Only analysts and above can create lab reports
        if user.role in ['admin', 'administrador', 'supervisor', 'analyst']:
            return True
        
        return False
