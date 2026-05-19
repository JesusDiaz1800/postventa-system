import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, Sum, F, Value, CharField
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone
from apps.visits.models import VisitReport, VisitStatus, InstallationLevel

logger = logging.getLogger(__name__)

class VisitMetrics:
    """Dashboard metrics for VisitReports (SERTEC System) - Professional Business Intelligence Rebuild"""
    
    def __init__(self):
        self.now = timezone.now()
        self.today = self.now.date()
    
    def get_kpis(self) -> Dict:
        try:
            total = VisitReport.objects.count()
            # Sincronización SAP (Pendientes)
            pending_sap = VisitReport.objects.filter(
                Q(sync_status='pending') | Q(sync_status='error'),
                status=VisitStatus.APPROVED
            ).count()
            # Visitas de esta semana
            this_week_start = self.now - timedelta(days=self.now.weekday())
            visits_this_week = VisitReport.objects.filter(visit_date__gte=this_week_start).count()
            
            # Tasa de aprobación
            approved_count = VisitReport.objects.filter(status=VisitStatus.APPROVED).count()
            approval_rate = (approved_count / total * 100) if total > 0 else 0

            return {
                'total_visits': total,
                'pending_sap_sync': pending_sap,
                'visits_this_week': visits_this_week,
                'approval_rate': round(approval_rate, 1)
            }
        except Exception as e:
            logger.error(f"Error getting kpis: {e}")
            return {}

    def get_distributions(self) -> Dict:
        try:
            # Clientes con más visitas
            by_client = VisitReport.objects.values('client_name').annotate(
                count=Count('id')
            ).order_by('-count')[:8]
            
            # Top Obras (Proyectos)
            by_project = VisitReport.objects.values('project_name').annotate(
                count=Count('id')
            ).order_by('-count')[:8]
            
            # Ranking de Técnicos (Productividad)
            by_tech = VisitReport.objects.values('technician').annotate(
                count=Count('id')
            ).order_by('-count')[:8]

            # Distribución Geográfica (Ciudad) - Formateado para visualización Power BI
            by_city = VisitReport.objects.values('city').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Flujo de visitas (Tendencia 30 días)
            start_date = self.now - timedelta(days=30)
            daily = VisitReport.objects.filter(
                visit_date__gte=start_date
            ).annotate(
                day=TruncDate('visit_date')
            ).values('day').annotate(count=Count('id')).order_by('day')

            trends = []
            for item in daily:
                if item['day']:
                    trends.append({
                        'date': item['day'].strftime('%d/%m'),
                        'count': item['count']
                    })

            return {
                'by_client': list(by_client),
                'by_project': list(by_project),
                'by_technician': list(by_tech),
                'by_city': list(by_city),
                'trends': trends
            }
        except Exception as e:
            logger.error(f"Error getting distributions: {e}")
            return {}

    def get_activity_feed(self, limit: int = 10) -> List:
        """Registro detallado de actividad"""
        try:
            latest = VisitReport.objects.order_by('-created_at')[:limit]
            return [{
                'id': r.id,
                'report': r.report_number,
                'project': r.project_name,
                'client': r.client_name,
                'tech': r.technician,
                'status': r.status,
                'time': r.created_at.isoformat()
            } for r in latest]
        except Exception as e:
            logger.error(f"Error getting activity feed: {e}")
            return []

    def get_comprehensive_dashboard(self) -> Dict:
        return {
            'kpis': self.get_kpis(),
            'distributions': self.get_distributions(),
            'feed': self.get_activity_feed(),
            'generated_at': self.now.isoformat()
        }

visit_metrics = VisitMetrics()
