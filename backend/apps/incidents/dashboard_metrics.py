"""
Dashboard metrics and KPIs for incident management
Provides comprehensive analytics and reporting
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, Sum, F, Value, CharField
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek, Concat
from django.utils import timezone
from .models import Incident, IncidentImage
from apps.users.models import User
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)

class DashboardMetrics:
    """Dashboard metrics and KPIs calculator"""
    
    def __init__(self):
        self.now = timezone.now()
        self.today = self.now.date()
        self.this_month = self.now.replace(day=1)
        self.this_year = self.now.replace(month=1, day=1)
    
    def get_overview_metrics(self) -> Dict:
        """Get overview metrics for dashboard"""
        try:
            # Total incidents
            total_incidents = Incident.objects.count()
            
            # Incidents by status (model uses 'estado')
            incidents_by_status = Incident.objects.values('estado').annotate(count=Count('id'))
            status_counts = {item['estado']: item['count'] for item in incidents_by_status}
            
            # Incidents by priority (model uses 'prioridad')
            incidents_by_priority = Incident.objects.values('prioridad').annotate(count=Count('id'))
            priority_counts = {item['prioridad']: item['count'] for item in incidents_by_priority}
            
            # Recent incidents (last 7 days)
            recent_incidents = Incident.objects.filter(
                created_at__gte=self.now - timedelta(days=7)
            ).count()
            
            # Pending incidents (non-cerrado estados: abierto, reporte_visita, calidad, proveedor)
            pending_incidents = Incident.objects.filter(
                estado__in=['abierto', 'reporte_visita', 'calidad', 'proveedor']
            ).count()
            
            # Overdue incidents
            overdue_incidents = Incident.objects.filter(
                estado__in=['abierto', 'reporte_visita', 'calidad', 'proveedor'],
                fecha_deteccion__lt=self.now - timedelta(days=30)
            ).count()
            
            return {
                'total_incidents': total_incidents,
                'recent_incidents': recent_incidents,
                'pending_incidents': pending_incidents,
                'overdue_incidents': overdue_incidents,
                'incidents_by_status': status_counts,
                'incidents_by_priority': priority_counts,
                'completion_rate': self._calculate_completion_rate(),
                'average_resolution_time': self._calculate_average_resolution_time()
            }
            
        except Exception as e:
            logger.error(f"Error getting overview metrics: {e}")
            return {}
    
    def get_incident_trends(self, days: int = 30) -> Dict:
        """Get incident trends over time"""
        try:
            start_date = self.now - timedelta(days=days)
            
            # Daily incident counts using TruncDate (DB agnostic)
            daily_incidents = Incident.objects.filter(
                created_at__gte=start_date
            ).annotate(
                day=TruncDate('created_at')
            ).values('day').annotate(count=Count('id')).order_by('day')
            
            # Weekly incident counts using TruncWeek
            weekly_incidents = Incident.objects.filter(
                created_at__gte=start_date
            ).annotate(
                week=TruncWeek('created_at')
            ).values('week').annotate(count=Count('id')).order_by('week')
            
            # Monthly incident counts using TruncMonth
            monthly_incidents = Incident.objects.filter(
                created_at__gte=start_date
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(count=Count('id')).order_by('month')
            
            # Convert QuerySets to list and format dates for JSON serialization
            daily_data = []
            for item in daily_incidents:
                daily_data.append({
                    'day': item['day'].strftime('%Y-%m-%d') if item['day'] else None,
                    'count': item['count']
                })
                
            weekly_data = []
            for item in weekly_incidents:
                weekly_data.append({
                    'week': item['week'].strftime('%Y-%W') if item['week'] else None,
                    'count': item['count']
                })
                
            monthly_data = []
            for item in monthly_incidents:
                monthly_data.append({
                    'month': item['month'].strftime('%Y-%m') if item['month'] else None,
                    'count': item['count']
                })
            
            return {
                'daily_trends': daily_data,
                'weekly_trends': weekly_data,
                'monthly_trends': monthly_data,
                'trend_period': f"{days} days"
            }
            
        except Exception as e:
            logger.error(f"Error getting incident trends: {e}")
            return {}
    
    def get_sku_analysis(self) -> Dict:
        """Get SKU analysis and statistics"""
        try:
            # Top problematic SKUs (model uses resolution_time_hours)
            top_problematic_skus = Incident.objects.values('sku').annotate(
                incident_count=Count('id'),
                avg_resolution_time=Avg('resolution_time_hours')
            ).order_by('-incident_count')[:10]
            
            # SKUs by incident count (is_re_incident not in model, simplified)
            sku_reincident_rate = Incident.objects.values('sku').annotate(
                total_incidents=Count('id')
            ).order_by('-total_incidents')[:10]
            
            # SKUs by category
            skus_by_category = Incident.objects.values('categoria', 'sku').annotate(
                count=Count('id')
            ).order_by('categoria', '-count')
            
            return {
                'top_problematic_skus': list(top_problematic_skus),
                'sku_reincident_rates': list(sku_reincident_rate),
                'skus_by_category': list(skus_by_category)
            }
            
        except Exception as e:
            logger.error(f"Error getting SKU analysis: {e}")
            return {}
    
    def get_batch_analysis(self) -> Dict:
        """Get batch analysis and statistics"""
        try:
            # Top problematic batches
            top_problematic_batches = Incident.objects.values('lote').annotate(
                incident_count=Count('id'),
                affected_skus=Count('sku', distinct=True)
            ).order_by('-incident_count')[:10]
            
            # Batch quality trends (categoria is FK, use categoria__name)
            batch_quality_trends = Incident.objects.values('lote').annotate(
                total_incidents=Count('id'),
                quality_issues=Count('id', filter=Q(categoria__name__icontains='calidad'))
            ).filter(total_incidents__gt=0).annotate(
                quality_issue_rate=100.0 * F('quality_issues') / F('total_incidents')
            ).order_by('-quality_issue_rate')[:10]
            
            return {
                'top_problematic_batches': list(top_problematic_batches),
                'batch_quality_trends': list(batch_quality_trends)
            }
            
        except Exception as e:
            logger.error(f"Error getting batch analysis: {e}")
            return {}
    
    def get_user_performance(self) -> Dict:
        """Get user performance metrics"""
        try:
            # User incident handling (model: estado='cerrado', resolution_time_hours)
            user_incidents = Incident.objects.values('assigned_to__username').annotate(
                total_incidents=Count('id'),
                resolved_incidents=Count('id', filter=Q(estado='cerrado')),
                avg_resolution_time=Avg('resolution_time_hours')
            ).order_by('-total_incidents')
            
            # User response times (response_time not in model, use resolution_time_hours)
            user_response_times = Incident.objects.values('assigned_to__username').annotate(
                avg_resolution_time=Avg('resolution_time_hours')
            ).order_by('avg_resolution_time')
            
            # User workload (pending = non-cerrado)
            user_workload = Incident.objects.filter(
                estado__in=['abierto', 'reporte_visita', 'calidad', 'proveedor']
            ).values('assigned_to__username').annotate(
                pending_incidents=Count('id')
            ).order_by('-pending_incidents')
            
            return {
                'user_incident_handling': list(user_incidents),
                'user_response_times': list(user_response_times),
                'user_workload': list(user_workload)
            }
            
        except Exception as e:
            logger.error(f"Error getting user performance: {e}")
            return {}
    
    def get_category_analysis(self) -> Dict:
        """Get incident category analysis"""
        try:
            # Incidents by category (model uses resolution_time_hours)
            incidents_by_category = Incident.objects.values('categoria').annotate(
                count=Count('id'),
                avg_resolution_time=Avg('resolution_time_hours')
            ).order_by('-count')
            
            # Incidents by subcategory
            incidents_by_subcategory = Incident.objects.values('categoria', 'subcategoria').annotate(
                count=Count('id')
            ).order_by('categoria', '-count')
            
            # Category trends over time
            category_trends = Incident.objects.filter(
                created_at__gte=self.now - timedelta(days=30)
            ).values('categoria').annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'incidents_by_category': list(incidents_by_category),
                'incidents_by_subcategory': list(incidents_by_subcategory),
                'category_trends': list(category_trends)
            }
            
        except Exception as e:
            logger.error(f"Error getting category analysis: {e}")
            return {}
    
    def get_resolution_metrics(self) -> Dict:
        """Get resolution metrics and KPIs"""
        try:
            # Average resolution time by category (model: estado, resolution_time_hours)
            resolution_by_category = Incident.objects.values('categoria').annotate(
                avg_resolution_time=Avg('resolution_time_hours'),
                count=Count('id')
            ).order_by('avg_resolution_time')
            
            # Resolution time trends
            resolution_trends = Incident.objects.filter(
                estado='cerrado',
                created_at__gte=self.now - timedelta(days=30)
            ).annotate(
                week=TruncWeek('created_at')
            ).values('week').annotate(
                avg_resolution_time=Avg('resolution_time_hours')
            ).order_by('week')
            
            # Format dates for JSON
            resolution_trends_data = []
            for item in resolution_trends:
                resolution_trends_data.append({
                    'week': item['week'].strftime('%Y-%W') if item['week'] else None,
                    'avg_resolution_time': item['avg_resolution_time']
                })
            
            # First-time resolution rate (is_re_incident not in model, use total cerrados)
            first_time_resolution = Incident.objects.filter(
                estado='cerrado'
            ).aggregate(
                total_resolved=Count('id'),
                first_time_resolved=Count('id')
            )
            
            first_time_rate = 0
            if first_time_resolution['total_resolved'] > 0:
                first_time_rate = (first_time_resolution['first_time_resolved'] / 
                                 first_time_resolution['total_resolved']) * 100
            
            return {
                'resolution_by_category': list(resolution_by_category),
                'resolution_trends': resolution_trends_data,
                'first_time_resolution_rate': first_time_rate,
                'total_resolved': first_time_resolution['total_resolved'],
                'first_time_resolved': first_time_resolution['first_time_resolved']
            }
            
        except Exception as e:
            logger.error(f"Error getting resolution metrics: {e}")
            return {}
    
    def get_ai_analysis_metrics(self) -> Dict:
        """Get AI analysis metrics"""
        try:
            # Incidents with AI analysis
            incidents_with_ai = Incident.objects.filter(
                ai_analysis__isnull=False
            ).count()
            
            total_incidents = Incident.objects.count()
            ai_usage_rate = 0
            if total_incidents > 0:
                ai_usage_rate = (incidents_with_ai / total_incidents) * 100
            
            # AI analysis accuracy (based on user feedback)
            ai_accuracy = Incident.objects.filter(
                ai_analysis__isnull=False,
                ai_analysis_accuracy__isnull=False
            ).aggregate(
                avg_accuracy=Avg('ai_analysis_accuracy')
            )
            
            # AI analysis by category
            ai_by_category = Incident.objects.filter(
                ai_analysis__isnull=False
            ).values('categoria').annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'incidents_with_ai': incidents_with_ai,
                'total_incidents': total_incidents,
                'ai_usage_rate': ai_usage_rate,
                'ai_accuracy': ai_accuracy.get('avg_accuracy', 0),
                'ai_by_category': list(ai_by_category)
            }
            
        except Exception as e:
            logger.error(f"Error getting AI analysis metrics: {e}")
            return {}
    
    def get_document_metrics(self) -> Dict:
        """Get document generation metrics"""
        try:
            # Documents generated from existing tables
            from apps.documents.models import VisitReport, SupplierReport, LabReport, QualityReport
            
            visit_count = VisitReport.objects.count()
            supplier_count = SupplierReport.objects.count()
            lab_count = LabReport.objects.count()
            quality_count = QualityReport.objects.count()
            
            total_documents = visit_count + supplier_count + lab_count + quality_count
            
            documents_by_type = [
                {'document_type': 'visit_report', 'count': visit_count},
                {'document_type': 'supplier_report', 'count': supplier_count},
                {'document_type': 'lab_report', 'count': lab_count},
                {'document_type': 'quality_report', 'count': quality_count}
            ]
            
            # Recent document generation (Optimized)
            recent_date = self.now - timedelta(days=7)
            recent_visits = VisitReport.objects.filter(created_at__gte=recent_date).count()
            recent_suppliers = SupplierReport.objects.filter(created_at__gte=recent_date).count()
            recent_labs = LabReport.objects.filter(created_at__gte=recent_date).count()
            recent_quality = QualityReport.objects.filter(created_at__gte=recent_date).count()
            
            recent_documents = recent_visits + recent_suppliers + recent_labs + recent_quality
            
            # Document generation by incident (Optimized using annotations)
            # Annotate Incident with counts of each report type
            incidents_with_docs = Incident.objects.annotate(
                visit_count=Count('visitreport'),
                supplier_count=Count('supplierreport'),
                lab_count=Count('labreport'),
                quality_count=Count('qualityreport')
            ).annotate(
                total_docs=F('visit_count') + F('supplier_count') + F('lab_count') + F('quality_count')
            ).filter(
                total_docs__gt=0
            ).order_by('-total_docs')
            
            documents_per_incident = []
            for incident in incidents_with_docs:
                documents_per_incident.append({
                    'incident_id': incident.id,
                    'count': incident.total_docs
                })
            
            return {
                'total_documents': total_documents,
                'recent_documents': recent_documents,
                'documents_by_type': list(documents_by_type),
                'documents_per_incident': list(documents_per_incident)
            }
            
        except Exception as e:
            logger.error(f"Error getting document metrics: {e}")
            return {}
    
    def get_workflow_metrics(self) -> Dict:
        """Get workflow metrics - DISABLED: Workflows feature was removed"""
        # Workflows feature was removed from the system
        return {
            'total_workflows': 0,
            'active_workflows': 0,
            'completed_workflows': 0,
            'workflow_completion_rate': 0,
            'avg_workflow_duration': 0,
            'message': 'Workflows feature disabled'
        }
    
    def get_security_metrics(self) -> Dict:
        """Get security and audit metrics"""
        try:
            # Login attempts
            login_attempts = AuditLog.objects.filter(
                action='login',
                timestamp__gte=self.now - timedelta(days=7)
            ).count()
            
            # Failed login attempts
            failed_logins = AuditLog.objects.filter(
                action='login',
                success=False,
                timestamp__gte=self.now - timedelta(days=7)
            ).count()
            
            # Security events
            security_events = AuditLog.objects.filter(
                resource_type='security',
                timestamp__gte=self.now - timedelta(days=7)
            ).count()
            
            # User activity
            active_users = AuditLog.objects.filter(
                timestamp__gte=self.now - timedelta(days=7)
            ).values('user').distinct().count()
            
            return {
                'login_attempts': login_attempts,
                'failed_logins': failed_logins,
                'security_events': security_events,
                'active_users': active_users,
                'login_success_rate': ((login_attempts - failed_logins) / login_attempts * 100) if login_attempts > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return {}
    
    def _calculate_completion_rate(self) -> float:
        """Calculate incident completion rate"""
        try:
            total_incidents = Incident.objects.count()
            completed_incidents = Incident.objects.filter(estado='cerrado').count()
            
            if total_incidents > 0:
                return (completed_incidents / total_incidents) * 100
            return 0
            
        except Exception as e:
            logger.error(f"Error calculating completion rate: {e}")
            return 0
    
    def _calculate_average_resolution_time(self) -> float:
        """Calculate average resolution time in hours"""
        try:
            avg_time = Incident.objects.filter(
                estado='cerrado',
                resolution_time_hours__isnull=False
            ).aggregate(avg_time=Avg('resolution_time_hours'))
            
            if avg_time['avg_time']:
                return avg_time['avg_time'].total_seconds() / 3600  # Convert to hours
            return 0
            
        except Exception as e:
            logger.error(f"Error calculating average resolution time: {e}")
            return 0
    
    def get_comprehensive_dashboard(self) -> Dict:
        """Get comprehensive dashboard data"""
        try:
            # We could optimize this further by gathering all metrics in a parallel or fewer queries,
            # but for now, the individual query optimizations (N+1 fixes and DB agnostic functions) are a huge step up.
            return {
                'overview': self.get_overview_metrics(),
                'trends': self.get_incident_trends(),
                'sku_analysis': self.get_sku_analysis(),
                'batch_analysis': self.get_batch_analysis(),
                'user_performance': self.get_user_performance(),
                'category_analysis': self.get_category_analysis(),
                'resolution_metrics': self.get_resolution_metrics(),
                'ai_metrics': self.get_ai_analysis_metrics(),
                'document_metrics': self.get_document_metrics(),
                'workflow_metrics': self.get_workflow_metrics(),
                'security_metrics': self.get_security_metrics(),
                'generated_at': self.now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive dashboard: {e}")
            return {}

# Global instance
dashboard_metrics = DashboardMetrics()
