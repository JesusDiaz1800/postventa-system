import json
import logging
import hashlib
import os
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.files.storage import default_storage

from .models import (
    ReportTemplate, ReportInstance, ReportSchedule, 
    ReportDashboard, ReportWidget, ReportExport
)

logger = logging.getLogger(__name__)


class ReportService:
    """Servicio para gestionar reportes"""
    
    def __init__(self):
        self.reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        self.ensure_reports_directory()
    
    def ensure_reports_directory(self):
        """Asegurar que el directorio de reportes existe"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_report(self, template, config, user):
        """Generar reporte desde plantilla"""
        try:
            # Crear instancia de reporte
            instance = ReportInstance.objects.create(
                template=template,
                status='pending',
                custom_filters=config.get('custom_filters', {}),
                custom_config=config.get('custom_config', {}),
                requested_by=user,
                requested_at=timezone.now()
            )
            
            # Actualizar estado a generando
            instance.status = 'generating'
            instance.started_at = timezone.now()
            instance.save()
            
            # Generar reporte
            report_data = self._generate_report_data(instance, template, config)
            
            # Crear archivo
            file_path = self._create_report_file(instance, template, report_data)
            
            # Actualizar instancia
            instance.status = 'completed'
            instance.completed_at = timezone.now()
            instance.report_data = report_data
            instance.file_path = file_path
            instance.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            instance.file_hash = self._calculate_file_hash(file_path)
            instance.expires_at = timezone.now() + timedelta(days=template.retention_days)
            instance.save()
            
            # Enviar email si está configurado
            if config.get('email_recipients'):
                self._send_report_email(instance, config['email_recipients'])
            
            return instance
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            
            # Actualizar instancia con error
            instance.status = 'failed'
            instance.completed_at = timezone.now()
            instance.error_message = str(e)
            instance.error_details = {'error_type': type(e).__name__}
            instance.save()
            
            raise e
    
    def test_template(self, template, test_config):
        """Probar plantilla de reporte"""
        try:
            # Simular generación sin crear instancia
            mock_instance = type('MockInstance', (), {
                'template': template,
                'custom_filters': test_config.get('custom_filters', {}),
                'custom_config': test_config.get('custom_config', {}),
            })()
            
            # Generar datos de prueba
            report_data = self._generate_report_data(mock_instance, template, test_config)
            
            return {
                'success': True,
                'data_preview': report_data,
                'estimated_size': len(json.dumps(report_data)),
                'message': 'Plantilla probada exitosamente'
            }
            
        except Exception as e:
            logger.error(f"Error testing template: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error probando plantilla'
            }
    
    def cancel_report(self, instance, user):
        """Cancelar generación de reporte"""
        if instance.status not in ['pending', 'generating']:
            raise Exception("El reporte no puede ser cancelado en su estado actual")
        
        instance.status = 'cancelled'
        instance.completed_at = timezone.now()
        instance.save()
        
        # Limpiar archivos temporales si existen
        if instance.file_path and os.path.exists(instance.file_path):
            try:
                os.remove(instance.file_path)
            except Exception as e:
                logger.warning(f"Error removing temporary file: {str(e)}")
    
    def export_report(self, instance, export_config, user):
        """Exportar reporte en formato diferente"""
        try:
            # Crear exportación
            export = ReportExport.objects.create(
                instance=instance,
                export_format=export_config['export_format'],
                status='pending',
                export_config=export_config.get('export_config', {}),
                requested_by=user,
                requested_at=timezone.now()
            )
            
            # Actualizar estado a procesando
            export.status = 'processing'
            export.save()
            
            # Exportar archivo
            file_path = self._create_export_file(export, instance, export_config)
            
            # Actualizar exportación
            export.status = 'completed'
            export.completed_at = timezone.now()
            export.file_path = file_path
            export.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            export.file_hash = self._calculate_file_hash(file_path)
            export.save()
            
            return export
            
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            
            # Actualizar exportación con error
            export.status = 'failed'
            export.completed_at = timezone.now()
            export.error_message = str(e)
            export.error_details = {'error_type': type(e).__name__}
            export.save()
            
            raise e
    
    def execute_schedule(self, schedule, user):
        """Ejecutar programación de reporte"""
        try:
            # Crear instancia de reporte
            instance = ReportInstance.objects.create(
                template=schedule.template,
                status='pending',
                custom_filters={},
                custom_config={},
                requested_by=user,
                requested_at=timezone.now()
            )
            
            # Actualizar programación
            schedule.last_executed = timezone.now()
            schedule.save()
            
            # Generar reporte
            config = {
                'email_recipients': schedule.email_recipients,
                'webhook_url': schedule.webhook_url,
            }
            
            return self.generate_report(schedule.template, config, user)
            
        except Exception as e:
            logger.error(f"Error executing schedule: {str(e)}")
            raise e
    
    def _generate_report_data(self, instance, template, config):
        """Generar datos del reporte"""
        try:
            # Obtener datos según el tipo de reporte
            if template.report_type == 'incident_summary':
                return self._generate_incident_summary_data(instance, template, config)
            elif template.report_type == 'incident_trends':
                return self._generate_incident_trends_data(instance, template, config)
            elif template.report_type == 'user_activity':
                return self._generate_user_activity_data(instance, template, config)
            elif template.report_type == 'document_usage':
                return self._generate_document_usage_data(instance, template, config)
            elif template.report_type == 'workflow_performance':
                return self._generate_workflow_performance_data(instance, template, config)
            elif template.report_type == 'integration_status':
                return self._generate_integration_status_data(instance, template, config)
            elif template.report_type == 'audit_summary':
                return self._generate_audit_summary_data(instance, template, config)
            else:
                return self._generate_custom_report_data(instance, template, config)
                
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            raise e
    
    def _generate_incident_summary_data(self, instance, template, config):
        """Generar datos de resumen de incidentes"""
        # Implementar lógica específica para resumen de incidentes
        return {
            'title': 'Resumen de Incidentes',
            'period': 'Último mes',
            'total_incidents': 150,
            'resolved_incidents': 120,
            'pending_incidents': 30,
            'by_priority': {
                'high': 25,
                'medium': 75,
                'low': 50
            },
            'by_status': {
                'open': 30,
                'in_progress': 45,
                'resolved': 120,
                'closed': 115
            },
            'average_resolution_time': '2.5 días',
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_incident_trends_data(self, instance, template, config):
        """Generar datos de tendencias de incidentes"""
        # Implementar lógica específica para tendencias de incidentes
        return {
            'title': 'Tendencias de Incidentes',
            'period': 'Últimos 12 meses',
            'trends': [
                {'month': 'Ene', 'count': 45},
                {'month': 'Feb', 'count': 52},
                {'month': 'Mar', 'count': 38},
                {'month': 'Abr', 'count': 61},
                {'month': 'May', 'count': 47},
                {'month': 'Jun', 'count': 55},
            ],
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_user_activity_data(self, instance, template, config):
        """Generar datos de actividad de usuarios"""
        # Implementar lógica específica para actividad de usuarios
        return {
            'title': 'Actividad de Usuarios',
            'period': 'Última semana',
            'total_users': 25,
            'active_users': 18,
            'inactive_users': 7,
            'by_role': {
                'admin': 3,
                'manager': 5,
                'user': 17
            },
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_document_usage_data(self, instance, template, config):
        """Generar datos de uso de documentos"""
        # Implementar lógica específica para uso de documentos
        return {
            'title': 'Uso de Documentos',
            'period': 'Último mes',
            'total_documents': 500,
            'downloaded_documents': 350,
            'by_type': {
                'pdf': 200,
                'docx': 150,
                'xlsx': 100,
                'other': 50
            },
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_workflow_performance_data(self, instance, template, config):
        """Generar datos de rendimiento de workflows"""
        # Implementar lógica específica para rendimiento de workflows
        return {
            'title': 'Rendimiento de Workflows',
            'period': 'Último mes',
            'total_workflows': 100,
            'completed_workflows': 85,
            'failed_workflows': 10,
            'pending_workflows': 5,
            'average_completion_time': '1.2 días',
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_integration_status_data(self, instance, template, config):
        """Generar datos de estado de integraciones"""
        # Implementar lógica específica para estado de integraciones
        return {
            'title': 'Estado de Integraciones',
            'period': 'Último mes',
            'total_integrations': 15,
            'active_integrations': 12,
            'failed_integrations': 2,
            'pending_integrations': 1,
            'by_type': {
                'api': 8,
                'webhook': 4,
                'file': 3
            },
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_audit_summary_data(self, instance, template, config):
        """Generar datos de resumen de auditoría"""
        # Implementar lógica específica para resumen de auditoría
        return {
            'title': 'Resumen de Auditoría',
            'period': 'Último mes',
            'total_actions': 1000,
            'by_action': {
                'create': 300,
                'update': 400,
                'delete': 50,
                'view': 250
            },
            'by_user': {
                'admin': 200,
                'manager': 300,
                'user': 500
            },
            'generated_at': timezone.now().isoformat()
        }
    
    def _generate_custom_report_data(self, instance, template, config):
        """Generar datos de reporte personalizado"""
        # Implementar lógica específica para reportes personalizados
        return {
            'title': 'Reporte Personalizado',
            'period': 'Personalizado',
            'data': template.template_config.get('custom_data', {}),
            'generated_at': timezone.now().isoformat()
        }
    
    def _create_report_file(self, instance, template, report_data):
        """Crear archivo de reporte"""
        try:
            # Generar nombre de archivo único
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{template.name}_{timestamp}.{template.format}"
            file_path = os.path.join(self.reports_dir, filename)
            
            # Crear archivo según el formato
            if template.format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
            elif template.format == 'html':
                html_content = self._generate_html_report(report_data, template)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            else:
                # Para otros formatos, usar JSON como fallback
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error creating report file: {str(e)}")
            raise e
    
    def _create_export_file(self, export, instance, export_config):
        """Crear archivo de exportación"""
        try:
            # Generar nombre de archivo único
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{instance.template.name}_{timestamp}.{export.export_format}"
            file_path = os.path.join(self.reports_dir, filename)
            
            # Crear archivo según el formato de exportación
            if export.export_format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(instance.report_data, f, indent=2, ensure_ascii=False)
            elif export.export_format == 'html':
                html_content = self._generate_html_report(instance.report_data, instance.template)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            else:
                # Para otros formatos, usar JSON como fallback
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(instance.report_data, f, indent=2, ensure_ascii=False)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error creating export file: {str(e)}")
            raise e
    
    def _generate_html_report(self, report_data, template):
        """Generar reporte HTML"""
        try:
            context = {
                'report_data': report_data,
                'template': template,
                'generated_at': timezone.now(),
            }
            
            # Usar plantilla HTML personalizada si existe
            template_name = f"reports/{template.report_type}.html"
            try:
                return render_to_string(template_name, context)
            except:
                # Fallback a plantilla genérica
                return render_to_string('reports/generic.html', context)
                
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            # Fallback a HTML básico
            return f"""
            <html>
            <head><title>{report_data.get('title', 'Reporte')}</title></head>
            <body>
                <h1>{report_data.get('title', 'Reporte')}</h1>
                <pre>{json.dumps(report_data, indent=2, ensure_ascii=False)}</pre>
            </body>
            </html>
            """
    
    def _calculate_file_hash(self, file_path):
        """Calcular hash del archivo"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    return file_hash
            return ''
        except Exception as e:
            logger.error(f"Error calculating file hash: {str(e)}")
            return ''
    
    def _send_report_email(self, instance, recipients):
        """Enviar reporte por email"""
        try:
            subject = f"Reporte: {instance.template.name}"
            message = f"""
            El reporte "{instance.template.name}" ha sido generado exitosamente.
            
            Detalles:
            - Generado el: {instance.completed_at}
            - Tamaño: {instance.file_size} bytes
            - Formato: {instance.template.format}
            
            Puede descargar el reporte desde el sistema.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False,
            )
            
        except Exception as e:
            logger.error(f"Error sending report email: {str(e)}")


class DashboardService:
    """Servicio para gestionar dashboards"""
    
    def __init__(self):
        pass
    
    def get_dashboard_data(self, dashboard, filters):
        """Obtener datos del dashboard"""
        try:
            data = {
                'dashboard': {
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'description': dashboard.description,
                    'layout_config': dashboard.layout_config,
                    'filters_config': dashboard.filters_config,
                },
                'widgets': [],
                'metadata': {
                    'generated_at': timezone.now().isoformat(),
                    'filters_applied': filters,
                }
            }
            
            # Obtener datos de cada widget
            for widget in dashboard.widgets.filter(is_active=True).order_by('order'):
                widget_data = self.get_widget_data(widget, filters)
                data['widgets'].append(widget_data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise e
    
    def get_widget_data(self, widget, filters):
        """Obtener datos del widget"""
        try:
            data = {
                'id': widget.id,
                'name': widget.name,
                'description': widget.description,
                'widget_type': widget.widget_type,
                'position': widget.position,
                'size': widget.size,
                'config': widget.config,
                'data': {},
                'metadata': {
                    'generated_at': timezone.now().isoformat(),
                    'filters_applied': filters,
                }
            }
            
            # Generar datos según el tipo de widget
            if widget.widget_type == 'metric':
                data['data'] = self._generate_metric_data(widget, filters)
            elif widget.widget_type == 'chart':
                data['data'] = self._generate_chart_data(widget, filters)
            elif widget.widget_type == 'table':
                data['data'] = self._generate_table_data(widget, filters)
            elif widget.widget_type == 'gauge':
                data['data'] = self._generate_gauge_data(widget, filters)
            elif widget.widget_type == 'progress':
                data['data'] = self._generate_progress_data(widget, filters)
            else:
                data['data'] = self._generate_default_data(widget, filters)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting widget data: {str(e)}")
            raise e
    
    def refresh_dashboard(self, dashboard):
        """Refrescar dashboard"""
        try:
            # Limpiar caché si existe
            # Implementar lógica de limpieza de caché
            
            # Actualizar timestamp de actualización
            dashboard.updated_at = timezone.now()
            dashboard.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {str(e)}")
            raise e
    
    def _generate_metric_data(self, widget, filters):
        """Generar datos para widget de métrica"""
        # Implementar lógica específica para métricas
        return {
            'value': 150,
            'label': 'Total de Incidentes',
            'change': '+12%',
            'change_type': 'positive'
        }
    
    def _generate_chart_data(self, widget, filters):
        """Generar datos para widget de gráfico"""
        # Implementar lógica específica para gráficos
        return {
            'labels': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            'datasets': [{
                'label': 'Incidentes',
                'data': [45, 52, 38, 61, 47, 55],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        }
    
    def _generate_table_data(self, widget, filters):
        """Generar datos para widget de tabla"""
        # Implementar lógica específica para tablas
        return {
            'headers': ['ID', 'Título', 'Estado', 'Fecha'],
            'rows': [
                ['1', 'Incidente 1', 'Abierto', '2025-01-01'],
                ['2', 'Incidente 2', 'Cerrado', '2025-01-02'],
                ['3', 'Incidente 3', 'En Progreso', '2025-01-03'],
            ]
        }
    
    def _generate_gauge_data(self, widget, filters):
        """Generar datos para widget de medidor"""
        # Implementar lógica específica para medidores
        return {
            'value': 75,
            'max': 100,
            'label': 'Progreso',
            'color': 'green'
        }
    
    def _generate_progress_data(self, widget, filters):
        """Generar datos para widget de progreso"""
        # Implementar lógica específica para progreso
        return {
            'value': 60,
            'max': 100,
            'label': 'Completado',
            'percentage': 60
        }
    
    def _generate_default_data(self, widget, filters):
        """Generar datos por defecto para widget"""
        return {
            'message': 'Datos no disponibles',
            'type': 'info'
        }
