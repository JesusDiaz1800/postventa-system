from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    BackupJob, BackupInstance, RestoreJob, BackupSchedule, 
    BackupStorage, BackupLog, BackupPolicy
)
from .serializers import (
    BackupJobSerializer, BackupInstanceSerializer, RestoreJobSerializer,
    BackupScheduleSerializer, BackupStorageSerializer, BackupLogSerializer,
    BackupPolicySerializer, BackupExecutionSerializer, RestoreExecutionSerializer,
    BackupTestSerializer, BackupStatisticsSerializer
)
from .services import BackupService, RestoreService, StorageService

logger = logging.getLogger(__name__)


class BackupJobViewSet(viewsets.ModelViewSet):
    """ViewSet para BackupJob"""
    
    queryset = BackupJob.objects.all()
    serializer_class = BackupJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        backup_type = self.request.query_params.get('backup_type')
        if backup_type:
            queryset = queryset.filter(backup_type=backup_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        is_scheduled = self.request.query_params.get('is_scheduled')
        if is_scheduled is not None:
            queryset = queryset.filter(is_scheduled=is_scheduled.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Ejecutar trabajo de backup"""
        job = self.get_object()
        serializer = BackupExecutionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = BackupService()
                instance = service.execute_backup(job, serializer.validated_data, request.user)
                
                return Response({
                    'success': True,
                    'message': 'Backup iniciado exitosamente',
                    'instance_id': instance.id
                })
            except Exception as e:
                logger.error(f"Error executing backup job {job.name}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error ejecutando backup: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Probar trabajo de backup"""
        job = self.get_object()
        
        try:
            service = BackupService()
            result = service.test_backup(job, request.data)
            
            return Response({
                'success': True,
                'message': 'Prueba exitosa',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error testing backup job {job.name}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error en la prueba: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar trabajo de backup"""
        job = self.get_object()
        
        try:
            service = BackupService()
            service.cancel_backup(job, request.user)
            
            return Response({
                'success': True,
                'message': 'Backup cancelado exitosamente'
            })
        except Exception as e:
            logger.error(f"Error cancelling backup job {job.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error cancelando backup: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de trabajos de backup"""
        queryset = self.get_queryset()
        
        stats = {
            'total_jobs': queryset.count(),
            'active_jobs': queryset.filter(status='running').count(),
            'by_type': {},
            'by_status': {},
        }
        
        # Estadísticas por tipo
        for backup_type, _ in BackupJob.BACKUP_TYPES:
            count = queryset.filter(backup_type=backup_type).count()
            if count > 0:
                stats['by_type'][backup_type] = count
        
        # Estadísticas por estado
        for status_choice, _ in BackupJob.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            if count > 0:
                stats['by_status'][status_choice] = count
        
        return Response(stats)


class BackupInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet para BackupInstance"""
    
    queryset = BackupInstance.objects.all()
    serializer_class = BackupInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        job = self.request.query_params.get('job')
        if job:
            queryset = queryset.filter(job_id=job)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(started_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(started_at__lte=date_to)
        
        return queryset.order_by('-started_at')
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Descargar archivo de backup"""
        instance = self.get_object()
        
        if instance.status != 'completed' or not instance.backup_path:
            return Response({
                'error': 'Backup no disponible para descarga'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from django.http import FileResponse
            import os
            
            if os.path.exists(instance.backup_path):
                return FileResponse(
                    open(instance.backup_path, 'rb'),
                    as_attachment=True,
                    filename=f"backup_{instance.id}.zip"
                )
            else:
                return Response({
                    'error': 'Archivo de backup no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Error downloading backup {instance.id}: {str(e)}")
            return Response({
                'error': 'Error descargando archivo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verificar integridad del backup"""
        instance = self.get_object()
        
        try:
            service = BackupService()
            result = service.verify_backup(instance)
            
            return Response({
                'success': True,
                'message': 'Verificación completada',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error verifying backup {instance.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error verificando backup: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de instancias de backup"""
        queryset = self.get_queryset()
        
        # Filtros de fecha
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(started_at__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(started_at__lte=date_to)
        
        stats = {
            'total_instances': queryset.count(),
            'by_status': {},
            'by_job': {},
            'success_rate': 0,
            'total_size': 0,
            'average_duration': 0,
        }
        
        # Estadísticas por estado
        for status_choice, _ in BackupInstance.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            if count > 0:
                stats['by_status'][status_choice] = count
        
        # Estadísticas por trabajo
        job_stats = queryset.values('job__name').annotate(count=Count('id'))
        for item in job_stats:
            stats['by_job'][item['job__name']] = item['count']
        
        # Tasa de éxito
        successful = queryset.filter(status='completed').count()
        total = queryset.count()
        if total > 0:
            stats['success_rate'] = (successful / total) * 100
        
        # Tamaño total
        total_size = queryset.aggregate(total=Sum('backup_size'))['total']
        if total_size:
            stats['total_size'] = total_size
        
        return Response(stats)


class RestoreJobViewSet(viewsets.ModelViewSet):
    """ViewSet para RestoreJob"""
    
    queryset = RestoreJob.objects.all()
    serializer_class = RestoreJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        backup_instance = self.request.query_params.get('backup_instance')
        if backup_instance:
            queryset = queryset.filter(backup_instance_id=backup_instance)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Ejecutar trabajo de restauración"""
        restore_job = self.get_object()
        serializer = RestoreExecutionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = RestoreService()
                result = service.execute_restore(restore_job, serializer.validated_data, request.user)
                
                return Response({
                    'success': True,
                    'message': 'Restauración iniciada exitosamente',
                    'data': result
                })
            except Exception as e:
                logger.error(f"Error executing restore job {restore_job.id}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error ejecutando restauración: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar trabajo de restauración"""
        restore_job = self.get_object()
        
        if restore_job.status not in ['pending', 'running']:
            return Response({
                'success': False,
                'message': 'La restauración no puede ser cancelada en su estado actual'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = RestoreService()
            service.cancel_restore(restore_job, request.user)
            
            return Response({
                'success': True,
                'message': 'Restauración cancelada exitosamente'
            })
        except Exception as e:
            logger.error(f"Error cancelling restore job {restore_job.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error cancelando restauración: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class BackupScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet para BackupSchedule"""
    
    queryset = BackupSchedule.objects.all()
    serializer_class = BackupScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        job = self.request.query_params.get('job')
        if job:
            queryset = queryset.filter(job_id=job)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def execute_now(self, request, pk=None):
        """Ejecutar programación inmediatamente"""
        schedule = self.get_object()
        
        try:
            service = BackupService()
            instance = service.execute_schedule(schedule, request.user)
            
            return Response({
                'success': True,
                'message': 'Programación ejecutada exitosamente',
                'instance_id': instance.id
            })
        except Exception as e:
            logger.error(f"Error executing schedule {schedule.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error ejecutando programación: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pausar programación"""
        schedule = self.get_object()
        
        if schedule.status != 'active':
            return Response({
                'success': False,
                'message': 'Solo se pueden pausar programaciones activas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        schedule.status = 'paused'
        schedule.save()
        
        return Response({
            'success': True,
            'message': 'Programación pausada exitosamente'
        })
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Reanudar programación"""
        schedule = self.get_object()
        
        if schedule.status != 'paused':
            return Response({
                'success': False,
                'message': 'Solo se pueden reanudar programaciones pausadas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        schedule.status = 'active'
        schedule.save()
        
        return Response({
            'success': True,
            'message': 'Programación reanudada exitosamente'
        })


class BackupStorageViewSet(viewsets.ModelViewSet):
    """ViewSet para BackupStorage"""
    
    queryset = BackupStorage.objects.all()
    serializer_class = BackupStorageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        storage_type = self.request.query_params.get('storage_type')
        if storage_type:
            queryset = queryset.filter(storage_type=storage_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Probar almacenamiento"""
        storage = self.get_object()
        serializer = BackupTestSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = StorageService()
                result = service.test_storage(storage, serializer.validated_data)
                
                return Response({
                    'success': True,
                    'message': 'Prueba exitosa',
                    'data': result
                })
            except Exception as e:
                logger.error(f"Error testing storage {storage.name}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error probando almacenamiento: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de almacenamientos"""
        queryset = self.get_queryset()
        
        stats = {
            'total_storages': queryset.count(),
            'active_storages': queryset.filter(is_active=True).count(),
            'by_type': {},
        }
        
        # Estadísticas por tipo
        for storage_type, _ in BackupStorage.STORAGE_TYPES:
            count = queryset.filter(storage_type=storage_type).count()
            if count > 0:
                stats['by_type'][storage_type] = count
        
        return Response(stats)


class BackupLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para BackupLog"""
    
    queryset = BackupLog.objects.all()
    serializer_class = BackupLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        job = self.request.query_params.get('job')
        if job:
            queryset = queryset.filter(job_id=job)
        
        instance = self.request.query_params.get('instance')
        if instance:
            queryset = queryset.filter(instance_id=instance)
        
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        step = self.request.query_params.get('step')
        if step:
            queryset = queryset.filter(step__icontains=step)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset.order_by('-timestamp')


class BackupPolicyViewSet(viewsets.ModelViewSet):
    """ViewSet para BackupPolicy"""
    
    queryset = BackupPolicy.objects.all()
    serializer_class = BackupPolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        policy_type = self.request.query_params.get('policy_type')
        if policy_type:
            queryset = queryset.filter(policy_type=policy_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-priority', 'name')
