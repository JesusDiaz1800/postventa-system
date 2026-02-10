from .models import AuditLog
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

class AuditService:
    """Servicio para gestión de auditoría (Simplificado)"""
    
    @staticmethod
    def log_action(user, action, description=None, ip_address=None, details=None):
        """Registrar acción en el log de auditoría"""
        try:
            return AuditLog.objects.create(
                user=user,
                action=action,
                description=description or f'Acción {action} realizada',
                ip_address=ip_address,
                details=details or {},
                timestamp=timezone.now()
            )
        except Exception as e:
            print(f"Error logging action: {e}")
            return None

    @staticmethod
    def get_audit_stats():
        """Obtener estadísticas básicas"""
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        
        return {
            'total_logs': AuditLog.objects.count(),
            'logs_today': AuditLog.objects.filter(timestamp__date=today).count(),
            'logs_this_week': AuditLog.objects.filter(timestamp__gte=week_ago).count(),
        }
