from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count, Avg, Max, Min
from datetime import timedelta
from .models import AuditLog, AuditRule, AuditReport, AuditAlert

# NotificationService importado condicionalmente para evitar importaciones circulares
NotificationService = None

def get_notification_service():
    """Obtener NotificationService de forma lazy para evitar importaciones circulares"""
    global NotificationService
    if NotificationService is None:
        try:
            from apps.notifications.services import NotificationService as NS
            NotificationService = NS
        except ImportError:
            class MockNotificationService:
                @staticmethod
                def create_notification(*args, **kwargs):
                    print(f"Notification (service not available): {kwargs.get('title', 'Unknown')} - {kwargs.get('message', 'Unknown')}")
                    return None
            NotificationService = MockNotificationService
    return NotificationService


class AuditService:
    """Servicio para gestión de auditoría"""
    
    @staticmethod
    def log_action(action, description, user=None, result='success', **kwargs):
        """Registrar acción en el log de auditoría"""
        audit_log = AuditLog.objects.create(
            action=action,
            description=description,
            user=user,
            result=result,
            **kwargs
        )
        
        # Verificar reglas de auditoría
        AuditService.check_audit_rules(audit_log)
        
        return audit_log
    
    @staticmethod
    def check_audit_rules(audit_log):
        """Verificar reglas de auditoría"""
        rules = AuditRule.objects.filter(is_active=True).order_by('-priority')
        
        for rule in rules:
            if AuditService.matches_rule(audit_log, rule):
                if rule.rule_type == 'alert':
                    AuditService.create_alert(audit_log, rule)
                elif rule.rule_type == 'block':
                    # Implementar lógica de bloqueo
                    pass
    
    @staticmethod
    def matches_rule(audit_log, rule):
        """Verificar si un log coincide con una regla"""
        if rule.action_filter and audit_log.action != rule.action_filter:
            return False
        
        if rule.user_filter:
            # Implementar lógica de filtro de usuario
            pass
        
        if rule.ip_filter:
            # Implementar lógica de filtro de IP
            pass
        
        if rule.module_filter and audit_log.module != rule.module_filter:
            return False
        
        if rule.severity_filter and audit_log.severity != rule.severity_filter:
            return False
        
        if rule.category_filter and audit_log.category != rule.category_filter:
            return False
        
        return True
    
    @staticmethod
    def create_alert(audit_log, rule):
        """Crear alerta de auditoría"""
        alert = AuditAlert.objects.create(
            title=f"Alerta de Auditoría: {audit_log.get_action_display()}",
            description=f"Se detectó una acción sospechosa: {audit_log.description}",
            severity=audit_log.severity,
            audit_log=audit_log
        )
        
        # Enviar notificación
        if rule.alert_email:
            notification_service = get_notification_service()
            notification_service.create_notification(
                user=User.objects.filter(email=rule.alert_email).first(),
                title=alert.title,
                message=alert.description,
                notification_type='system_alert',
                is_important=True
            )
        
        return alert
    
    @staticmethod
    def search_audit_logs(search_params):
        """Buscar registros de auditoría"""
        queryset = AuditLog.objects.all()
        
        # Filtros básicos
        if search_params.get('query'):
            query = search_params['query']
            queryset = queryset.filter(
                Q(description__icontains=query) |
                Q(action__icontains=query) |
                Q(module__icontains=query) |
                Q(function__icontains=query)
            )
        
        if search_params.get('action'):
            queryset = queryset.filter(action=search_params['action'])
        
        if search_params.get('result'):
            queryset = queryset.filter(result=search_params['result'])
        
        if search_params.get('user'):
            queryset = queryset.filter(user_id=search_params['user'])
        
        if search_params.get('severity'):
            queryset = queryset.filter(severity=search_params['severity'])
        
        if search_params.get('category'):
            queryset = queryset.filter(category=search_params['category'])
        
        if search_params.get('ip_address'):
            queryset = queryset.filter(ip_address=search_params['ip_address'])
        
        if search_params.get('module'):
            queryset = queryset.filter(module=search_params['module'])
        
        # Filtros de fecha
        if search_params.get('date_from'):
            queryset = queryset.filter(timestamp__gte=search_params['date_from'])
        
        if search_params.get('date_to'):
            queryset = queryset.filter(timestamp__lte=search_params['date_to'])
        
        # Ordenamiento
        ordering = search_params.get('ordering', '-timestamp')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    @staticmethod
    def export_audit_logs(export_params):
        """Exportar registros de auditoría"""
        queryset = AuditLog.objects.all()
        
        # Aplicar filtros
        if export_params.get('date_from'):
            queryset = queryset.filter(timestamp__gte=export_params['date_from'])
        
        if export_params.get('date_to'):
            queryset = queryset.filter(timestamp__lte=export_params['date_to'])
        
        if export_params.get('filters'):
            filters = export_params['filters']
            if filters.get('action'):
                queryset = queryset.filter(action=filters['action'])
            if filters.get('user'):
                queryset = queryset.filter(user_id=filters['user'])
            if filters.get('severity'):
                queryset = queryset.filter(severity=filters['severity'])
            if filters.get('category'):
                queryset = queryset.filter(category=filters['category'])
        
        return queryset
    
    @staticmethod
    def get_audit_stats():
        """Obtener estadísticas de auditoría"""
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Estadísticas básicas
        total_logs = AuditLog.objects.count()
        logs_today = AuditLog.objects.filter(timestamp__date=today).count()
        logs_this_week = AuditLog.objects.filter(timestamp__gte=week_ago).count()
        logs_this_month = AuditLog.objects.filter(timestamp__gte=month_ago).count()
        
        # Estadísticas de resultado
        successful_actions = AuditLog.objects.filter(result='success').count()
        failed_actions = AuditLog.objects.filter(result='failure').count()
        
        # Estadísticas de severidad
        high_severity_logs = AuditLog.objects.filter(severity='high').count()
        critical_logs = AuditLog.objects.filter(severity='critical').count()
        
        # Estadísticas por categoría
        logs_by_action = dict(AuditLog.objects.values_list('action').annotate(count=Count('id')).values_list('action', 'count'))
        logs_by_category = dict(AuditLog.objects.values_list('category').annotate(count=Count('id')).values_list('category', 'count'))
        logs_by_severity = dict(AuditLog.objects.values_list('severity').annotate(count=Count('id')).values_list('severity', 'count'))
        
        # Top usuarios
        logs_by_user = dict(AuditLog.objects.filter(user__isnull=False).values_list('user__username').annotate(count=Count('id')).values_list('user__username', 'count'))
        
        # Top IPs
        top_ips = dict(AuditLog.objects.filter(ip_address__isnull=False).values_list('ip_address').annotate(count=Count('id')).values_list('ip_address', 'count'))
        
        # Métricas de rendimiento
        avg_response_time = AuditLog.objects.filter(duration__isnull=False).aggregate(avg=Avg('duration'))['avg']
        
        # Tasa de error
        error_rate = (failed_actions / total_logs * 100) if total_logs > 0 else 0
        
        return {
            'total_logs': total_logs,
            'logs_today': logs_today,
            'logs_this_week': logs_this_week,
            'logs_this_month': logs_this_month,
            'successful_actions': successful_actions,
            'failed_actions': failed_actions,
            'high_severity_logs': high_severity_logs,
            'critical_logs': critical_logs,
            'logs_by_action': logs_by_action,
            'logs_by_category': logs_by_category,
            'logs_by_severity': logs_by_severity,
            'logs_by_user': logs_by_user,
            'top_ips': top_ips,
            'average_response_time': avg_response_time,
            'error_rate': error_rate
        }
    
    @staticmethod
    def get_real_time_data():
        """Obtener datos en tiempo real"""
        # Últimos 10 registros
        recent_logs = AuditLog.objects.order_by('-timestamp')[:10]
        
        # Estadísticas de la última hora
        hour_ago = timezone.now() - timedelta(hours=1)
        logs_last_hour = AuditLog.objects.filter(timestamp__gte=hour_ago)
        
        stats_last_hour = {
            'total': logs_last_hour.count(),
            'successful': logs_last_hour.filter(result='success').count(),
            'failed': logs_last_hour.filter(result='failure').count(),
            'high_severity': logs_last_hour.filter(severity__in=['high', 'critical']).count()
        }
        
        return {
            'recent_logs': recent_logs,
            'stats_last_hour': stats_last_hour
        }
    
    @staticmethod
    def get_audit_trends(period='24h'):
        """Obtener tendencias de auditoría"""
        if period == '24h':
            start_time = timezone.now() - timedelta(hours=24)
            interval = 'hour'
        elif period == '7d':
            start_time = timezone.now() - timedelta(days=7)
            interval = 'day'
        elif period == '30d':
            start_time = timezone.now() - timedelta(days=30)
            interval = 'day'
        else:
            start_time = timezone.now() - timedelta(hours=24)
            interval = 'hour'
        
        logs = AuditLog.objects.filter(timestamp__gte=start_time)
        
        # Agrupar por intervalo
        trends = []
        if interval == 'hour':
            for i in range(24):
                hour_start = start_time + timedelta(hours=i)
                hour_end = hour_start + timedelta(hours=1)
                hour_logs = logs.filter(timestamp__gte=hour_start, timestamp__lt=hour_end)
                
                trends.append({
                    'timestamp': hour_start.isoformat(),
                    'total': hour_logs.count(),
                    'successful': hour_logs.filter(result='success').count(),
                    'failed': hour_logs.filter(result='failure').count(),
                    'high_severity': hour_logs.filter(severity__in=['high', 'critical']).count()
                })
        
        return trends
    
    @staticmethod
    def get_top_users(limit=10):
        """Obtener top usuarios por actividad"""
        return AuditLog.objects.filter(user__isnull=False).values(
            'user__username', 'user__first_name', 'user__last_name'
        ).annotate(
            count=Count('id'),
            last_activity=Max('timestamp')
        ).order_by('-count')[:limit]
    
    @staticmethod
    def get_top_actions(limit=10):
        """Obtener top acciones"""
        return AuditLog.objects.values('action').annotate(
            count=Count('id'),
            last_occurrence=Max('timestamp')
        ).order_by('-count')[:limit]
    
    @staticmethod
    def get_security_events():
        """Obtener eventos de seguridad"""
        security_categories = ['authentication', 'authorization', 'security']
        security_actions = ['login', 'logout', 'unauthorized', 'forbidden']
        
        events = AuditLog.objects.filter(
            Q(category__in=security_categories) |
            Q(action__in=security_actions) |
            Q(severity__in=['high', 'critical'])
        ).order_by('-timestamp')[:50]
        
        return events
    
    @staticmethod
    def get_performance_metrics():
        """Obtener métricas de rendimiento"""
        # Métricas de tiempo de respuesta
        response_times = AuditLog.objects.filter(
            duration__isnull=False
        ).aggregate(
            avg=Avg('duration'),
            min=Min('duration'),
            max=Max('duration')
        )
        
        # Métricas por módulo
        module_metrics = AuditLog.objects.filter(
            module__isnull=False
        ).values('module').annotate(
            count=Count('id'),
            avg_duration=Avg('duration'),
            error_rate=Count('id', filter=Q(result='failure')) * 100.0 / Count('id')
        ).order_by('-count')[:10]
        
        return {
            'response_times': response_times,
            'module_metrics': module_metrics
        }
    
    @staticmethod
    def generate_audit_report(report):
        """Generar reporte de auditoría"""
        report.status = 'generating'
        report.save()
        
        try:
            # Aplicar filtros
            queryset = AuditLog.objects.all()
            
            if report.date_from:
                queryset = queryset.filter(timestamp__gte=report.date_from)
            
            if report.date_to:
                queryset = queryset.filter(timestamp__lte=report.date_to)
            
            if report.user_filter:
                queryset = queryset.filter(user__username__icontains=report.user_filter)
            
            if report.action_filter:
                queryset = queryset.filter(action=report.action_filter)
            
            if report.severity_filter:
                queryset = queryset.filter(severity=report.severity_filter)
            
            if report.category_filter:
                queryset = queryset.filter(category=report.category_filter)
            
            # Contar registros
            report.total_records = queryset.count()
            
            # Generar archivo (implementar según el tipo de reporte)
            # Por ahora solo marcamos como completado
            report.status = 'completed'
            report.completed_at = timezone.now()
            report.save()
            
        except Exception as e:
            report.status = 'failed'
            report.save()
            raise e
    
    @staticmethod
    def get_report_templates():
        """Obtener plantillas de reporte"""
        return [
            {
                'name': 'Reporte Diario',
                'description': 'Resumen de actividades del día',
                'report_type': 'daily',
                'filters': {
                    'date_from': timezone.now().date(),
                    'date_to': timezone.now().date()
                }
            },
            {
                'name': 'Reporte Semanal',
                'description': 'Resumen de actividades de la semana',
                'report_type': 'weekly',
                'filters': {
                    'date_from': timezone.now().date() - timedelta(days=7),
                    'date_to': timezone.now().date()
                }
            },
            {
                'name': 'Reporte de Seguridad',
                'description': 'Eventos de seguridad y accesos',
                'report_type': 'custom',
                'filters': {
                    'category': 'security',
                    'severity': 'high'
                }
            }
        ]
    
    @staticmethod
    def get_dashboard_data(dashboard, query_params):
        """Obtener datos del dashboard"""
        # Implementar lógica de widgets
        widgets_data = {}
        
        for widget_id, widget_config in dashboard.widgets_config.items():
            widget_type = widget_config.get('type')
            
            if widget_type == 'stats':
                widgets_data[widget_id] = AuditService.get_audit_stats()
            elif widget_type == 'recent_logs':
                limit = widget_config.get('limit', 10)
                widgets_data[widget_id] = AuditLog.objects.order_by('-timestamp')[:limit]
            elif widget_type == 'trends':
                period = widget_config.get('period', '24h')
                widgets_data[widget_id] = AuditService.get_audit_trends(period)
        
        return widgets_data
    
    @staticmethod
    def test_audit_rule(rule, test_data):
        """Probar regla de auditoría"""
        # Crear log de prueba
        test_log = AuditLog(
            action=test_data.get('action', 'test'),
            description=test_data.get('description', 'Test log'),
            result=test_data.get('result', 'success'),
            severity=test_data.get('severity', 'medium'),
            category=test_data.get('category', 'data_access'),
            module=test_data.get('module', 'test'),
            ip_address=test_data.get('ip_address'),
            user_id=test_data.get('user_id')
        )
        
        # Verificar si coincide con la regla
        matches = AuditService.matches_rule(test_log, rule)
        
        return {
            'matches': matches,
            'test_log': test_log,
            'rule': rule
        }
    
    @staticmethod
    def advanced_search(search_params):
        """Búsqueda avanzada"""
        # Implementar búsqueda avanzada con múltiples criterios
        queryset = AuditLog.objects.all()
        
        # Filtros complejos
        if search_params.get('date_range'):
            date_range = search_params['date_range']
            if date_range.get('from'):
                queryset = queryset.filter(timestamp__gte=date_range['from'])
            if date_range.get('to'):
                queryset = queryset.filter(timestamp__lte=date_range['to'])
        
        if search_params.get('users'):
            queryset = queryset.filter(user_id__in=search_params['users'])
        
        if search_params.get('actions'):
            queryset = queryset.filter(action__in=search_params['actions'])
        
        if search_params.get('severities'):
            queryset = queryset.filter(severity__in=search_params['severities'])
        
        if search_params.get('categories'):
            queryset = queryset.filter(category__in=search_params['categories'])
        
        if search_params.get('ip_addresses'):
            queryset = queryset.filter(ip_address__in=search_params['ip_addresses'])
        
        if search_params.get('modules'):
            queryset = queryset.filter(module__in=search_params['modules'])
        
        # Búsqueda de texto
        if search_params.get('text_search'):
            text = search_params['text_search']
            queryset = queryset.filter(
                Q(description__icontains=text) |
                Q(action__icontains=text) |
                Q(module__icontains=text) |
                Q(function__icontains=text)
            )
        
        # Ordenamiento
        ordering = search_params.get('ordering', '-timestamp')
        queryset = queryset.order_by(ordering)
        
        # Paginación
        page = search_params.get('page', 1)
        page_size = search_params.get('page_size', 50)
        offset = (page - 1) * page_size
        
        results = queryset[offset:offset + page_size]
        total = queryset.count()
        
        return {
            'results': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_next': offset + page_size < total,
            'has_previous': page > 1
        }
    
    @staticmethod
    def get_search_suggestions(query):
        """Obtener sugerencias de búsqueda"""
        suggestions = []
        
        if query:
            # Sugerencias de acciones
            actions = AuditLog.objects.filter(
                action__icontains=query
            ).values_list('action', flat=True).distinct()[:5]
            
            # Sugerencias de módulos
            modules = AuditLog.objects.filter(
                module__icontains=query
            ).values_list('module', flat=True).distinct()[:5]
            
            # Sugerencias de categorías
            categories = AuditLog.objects.filter(
                category__icontains=query
            ).values_list('category', flat=True).distinct()[:5]
            
            suggestions = {
                'actions': list(actions),
                'modules': list(modules),
                'categories': list(categories)
            }
        
        return suggestions
    
    @staticmethod
    def get_available_filters():
        """Obtener filtros disponibles"""
        return {
            'actions': list(AuditLog.objects.values_list('action', flat=True).distinct()),
            'results': list(AuditLog.objects.values_list('result', flat=True).distinct()),
            'severities': list(AuditLog.objects.values_list('severity', flat=True).distinct()),
            'categories': list(AuditLog.objects.values_list('category', flat=True).distinct()),
            'modules': list(AuditLog.objects.filter(module__isnull=False).values_list('module', flat=True).distinct()),
            'users': list(AuditLog.objects.filter(user__isnull=False).values_list('user__username', flat=True).distinct()),
            'ip_addresses': list(AuditLog.objects.filter(ip_address__isnull=False).values_list('ip_address', flat=True).distinct())
        }
