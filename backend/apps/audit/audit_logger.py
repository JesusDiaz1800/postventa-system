"""
Comprehensive audit logging system
Tracks all user actions, system events, and data changes
"""

import json
import logging
from typing import Dict, List, Optional, Any
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from .models import AuditLog

logger = logging.getLogger(__name__)
User = get_user_model()

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.enabled = True
        self.sensitive_fields = ['password', 'token', 'key', 'secret']
    
    def log_action(self, user, action: str, resource_type: str, resource_id: str = None,
                   resource_name: str = None, details: Dict = None, ip_address: str = None,
                   user_agent: str = None, success: bool = True, error_message: str = None):
        """
        Log a user action
        
        Args:
            user: User performing the action
            action: Action performed (create, read, update, delete, login, logout, etc.)
            resource_type: Type of resource (incident, document, user, etc.)
            resource_id: ID of the resource
            resource_name: Name of the resource
            details: Additional details about the action
            ip_address: IP address of the user
            user_agent: User agent string
            success: Whether the action was successful
            error_message: Error message if action failed
        """
        try:
            if not self.enabled:
                return
            
            # Sanitize details to remove sensitive information
            sanitized_details = self._sanitize_details(details) if details else {}
            
            # Map advanced fields to the simplified AuditLog model
            full_details = {
                **sanitized_details,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'resource_name': resource_name,
                'user_agent': user_agent,
                'success': success,
                'error_message': error_message
            }
            
            # Generate a human-readable description
            description = f"{action.replace('_', ' ').capitalize()} on {resource_type}"
            if resource_name:
                description += f": {resource_name}"
            if not success:
                description += f" (FAILED: {error_message})"
            
            # Create audit log entry - only with fields supported by models.py
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                description=description,
                details=full_details,
                ip_address=ip_address,
                timestamp=timezone.now()
            )
            
            # Log to file as well
            self._log_to_file(audit_log)
            
            logger.info(f"Audit log created: {action} on {resource_type} by {user.username if user else 'Anonymous'}")
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
    
    def log_login(self, user, ip_address: str = None, user_agent: str = None, success: bool = True, error_message: str = None):
        """Log user login attempt"""
        self.log_action(
            user=user,
            action='login',
            resource_type='user',
            resource_id=str(user.id) if user else None,
            resource_name=user.username if user else 'Unknown',
            details={'login_method': 'password'},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
    
    def log_logout(self, user, ip_address: str = None, user_agent: str = None):
        """Log user logout"""
        self.log_action(
            user=user,
            action='logout',
            resource_type='user',
            resource_id=str(user.id) if user else None,
            resource_name=user.username if user else 'Unknown',
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_incident_action(self, user, action: str, incident, details: Dict = None, ip_address: str = None, user_agent: str = None):
        """Log incident-related action"""
        self.log_action(
            user=user,
            action=action,
            resource_type='incident',
            resource_id=str(incident.id),
            resource_name=f"Incident {incident.id}",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_document_action(self, user, action: str, document, details: Dict = None, ip_address: str = None, user_agent: str = None):
        """Log document-related action"""
        # Intentar obtener un nombre descriptivo robusto para evitar AttributeError
        res_name = getattr(document, 'report_number', 
                   getattr(document, 'title', 
                   getattr(document, 'name', f"Document {document.id}")))
        
        self.log_action(
            user=user,
            action=action,
            resource_type='document',
            resource_id=str(document.id),
            resource_name=res_name,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

    
    def log_user_action(self, user, action: str, target_user, details: Dict = None, ip_address: str = None, user_agent: str = None):
        """Log user management action"""
        self.log_action(
            user=user,
            action=action,
            resource_type='user',
            resource_id=str(target_user.id),
            resource_name=target_user.username,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_workflow_action(self, user, action: str, workflow_instance, details: Dict = None, ip_address: str = None, user_agent: str = None):
        """Log workflow-related action"""
        self.log_action(
            user=user,
            action=action,
            resource_type='workflow',
            resource_id=str(workflow_instance.id),
            resource_name=f"Workflow {workflow_instance.workflow.name}",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_ai_action(self, user, action: str, resource_type: str, resource_id: str = None, details: Dict = None, ip_address: str = None, user_agent: str = None):
        """Log AI-related action"""
        self.log_action(
            user=user,
            action=action,
            resource_type=f'ai_{resource_type}',
            resource_id=resource_id,
            resource_name=f"AI {resource_type}",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_system_event(self, event_type: str, details: Dict = None, severity: str = 'info'):
        """Log system event"""
        self.log_action(
            user=None,
            action='system_event',
            resource_type='system',
            resource_name=event_type,
            details={**details, 'severity': severity} if details else {'severity': severity}
        )
    
    def log_security_event(self, event_type: str, user=None, details: Dict = None, ip_address: str = None, user_agent: str = None):
        """Log security-related event"""
        self.log_action(
            user=user,
            action='security_event',
            resource_type='security',
            resource_name=event_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False  # Security events are typically failures
        )
    
    def _sanitize_details(self, details: Dict) -> Dict:
        """Remove sensitive information from details"""
        try:
            sanitized = {}
            
            for key, value in details.items():
                # Check if key contains sensitive information
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    sanitized[key] = '[REDACTED]'
                elif isinstance(value, dict):
                    sanitized[key] = self._sanitize_details(value)
                elif isinstance(value, list):
                    sanitized[key] = [self._sanitize_details(item) if isinstance(item, dict) else item for item in value]
                else:
                    sanitized[key] = value
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing details: {e}")
            return details
    
    def _log_to_file(self, audit_log: AuditLog):
        """Log to file for additional backup"""
        try:
            # Extraer campos de details para el log de archivo
            details = audit_log.details or {}
            log_entry = {
                'timestamp': audit_log.timestamp.isoformat(),
                'user': audit_log.user.username if audit_log.user else 'Anonymous',
                'action': audit_log.action,
                'resource_type': details.get('resource_type'),
                'resource_id': details.get('resource_id'),
                'resource_name': details.get('resource_name'),
                'details': sanitized_details if hasattr(self, 'sanitized_details') else details,
                'ip_address': audit_log.ip_address,
                'user_agent': details.get('user_agent'),
                'success': details.get('success', True),
                'error_message': details.get('error_message')
            }
            
            # Log to file
            logger.info(f"AUDIT: {json.dumps(log_entry, cls=DjangoJSONEncoder)}")
            
        except Exception as e:
            logger.error(f"Error logging to file: {e}")
    
    def get_audit_trail(self, resource_type: str = None, resource_id: str = None, 
                       user_id: str = None, action: str = None, 
                       start_date=None, end_date=None, limit: int = 100) -> List[AuditLog]:
        """Get audit trail with filters"""
        try:
            queryset = AuditLog.objects.all()
            
            if resource_type:
                queryset = queryset.filter(details__resource_type=resource_type)
            
            if resource_id:
                queryset = queryset.filter(details__resource_id=resource_id)
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            if action:
                queryset = queryset.filter(action=action)
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            return queryset.order_by('-timestamp')[:limit]
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[AuditLog]:
        """Get user activity for specified days"""
        try:
            from datetime import timedelta
            start_date = timezone.now() - timedelta(days=days)
            
            return AuditLog.objects.filter(
                user_id=user_id,
                timestamp__gte=start_date
            ).order_by('-timestamp')
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return []
    
    def get_security_events(self, days: int = 7) -> List[AuditLog]:
        """Get security events for specified days"""
        try:
            from datetime import timedelta
            start_date = timezone.now() - timedelta(days=days)
            
            return AuditLog.objects.filter(
                details__resource_type='security',
                timestamp__gte=start_date
            ).order_by('-timestamp')
            
        except Exception as e:
            logger.error(f"Error getting security events: {e}")
            return []
    
    def get_failed_actions(self, days: int = 7) -> List[AuditLog]:
        """Get failed actions for specified days"""
        try:
            from datetime import timedelta
            start_date = timezone.now() - timedelta(days=days)
            
            return AuditLog.objects.filter(
                details__success=False,
                timestamp__gte=start_date
            ).order_by('-timestamp')
            
        except Exception as e:
            logger.error(f"Error getting failed actions: {e}")
            return []
    
    def get_audit_statistics(self, days: int = 30) -> Dict:
        """Get audit statistics for specified days"""
        try:
            from datetime import timedelta
            start_date = timezone.now() - timedelta(days=days)
            
            queryset = AuditLog.objects.filter(timestamp__gte=start_date)
            
            stats = {
                'total_actions': queryset.count(),
                'successful_actions': queryset.filter(details__success=True).count(),
                'failed_actions': queryset.filter(details__success=False).count(),
                'unique_users': queryset.values('user').distinct().count(),
                'actions_by_type': {},
                'actions_by_user': {},
                'security_events': queryset.filter(details__resource_type='security').count(),
                'login_attempts': queryset.filter(action='login').count(),
                'failed_logins': queryset.filter(action='login', details__success=False).count()
            }
            
            # Actions by type
            for action in queryset.values_list('action', flat=True).distinct():
                stats['actions_by_type'][action] = queryset.filter(action=action).count()
            
            # Actions by user
            for user in queryset.values_list('user__username', flat=True).distinct():
                if user:
                    stats['actions_by_user'][user] = queryset.filter(user__username=user).count()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting audit statistics: {e}")
            return {}
    
    def export_audit_logs(self, start_date=None, end_date=None, format: str = 'json') -> str:
        """Export audit logs in specified format"""
        try:
            queryset = AuditLog.objects.all()
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            logs = queryset.order_by('-timestamp')
            
            if format == 'json':
                return json.dumps([log.to_dict() for log in logs], cls=DjangoJSONEncoder, indent=2)
            elif format == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow(['timestamp', 'user', 'action', 'resource_type', 'resource_id', 
                               'resource_name', 'ip_address', 'success', 'error_message'])
                
                # Write data
                for log in logs:
                    det = log.details or {}
                    writer.writerow([
                        log.timestamp.isoformat(),
                        log.user.username if log.user else 'Anonymous',
                        log.action,
                        det.get('resource_type'),
                        det.get('resource_id'),
                        det.get('resource_name'),
                        log.ip_address,
                        det.get('success'),
                        det.get('error_message')
                    ])
                
                return output.getvalue()
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting audit logs: {e}")
            return ""
    
    def cleanup_old_logs(self, days: int = 365):
        """Clean up old audit logs"""
        try:
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=days)
            
            deleted_count = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
            
            logger.info(f"Cleaned up {deleted_count} old audit logs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return 0

# Global instance
audit_logger = AuditLogger()
