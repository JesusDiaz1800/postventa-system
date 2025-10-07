from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    BackupJob, BackupInstance, RestoreJob, BackupSchedule, 
    BackupStorage, BackupLog, BackupPolicy
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BackupJob)
def backup_job_post_save(sender, instance, created, **kwargs):
    """Señal post-save para BackupJob"""
    if created:
        logger.info(f"Nuevo trabajo de backup creado: {instance.name}")
        
        # Crear programación automática si está configurada
        if instance.is_scheduled and instance.schedule_config:
            schedule = BackupSchedule.objects.create(
                job=instance,
                name=f"Schedule for {instance.name}",
                description=f"Programación automática para {instance.name}",
                schedule_type=instance.schedule_config.get('schedule_type', 'daily'),
                schedule_config=instance.schedule_config,
                status='active',
                created_by=instance.created_by
            )
            logger.info(f"Programación automática creada: {schedule.name}")
    
    # Si se cambió el estado a 'active', verificar si hay programaciones
    if not created and instance.status == 'active':
        schedules = BackupSchedule.objects.filter(job=instance, status='paused')
        for schedule in schedules:
            schedule.status = 'active'
            schedule.save()
            logger.info(f"Programación reactivada: {schedule.name}")


@receiver(post_save, sender=BackupInstance)
def backup_instance_post_save(sender, instance, created, **kwargs):
    """Señal post-save para BackupInstance"""
    if created:
        logger.info(f"Nueva instancia de backup creada: {instance.id}")
        
        # Crear log de inicio
        BackupLog.objects.create(
            instance=instance,
            job=instance.job,
            level='info',
            step='created',
            message=f'Instancia de backup {instance.id} creada',
            timestamp=timezone.now()
        )
    
    # Si se completó el backup, verificar políticas de retención
    if not created and instance.status == 'completed':
        logger.info(f"Backup completado: {instance.id}")
        
        # Aplicar políticas de retención
        _apply_retention_policies(instance.job)
        
        # Crear log de finalización
        BackupLog.objects.create(
            instance=instance,
            job=instance.job,
            level='info',
            step='completed',
            message=f'Backup {instance.id} completado exitosamente',
            timestamp=timezone.now()
        )
    
    # Si falló el backup, registrar error
    elif not created and instance.status == 'failed':
        logger.error(f"Backup falló: {instance.id} - {instance.error_message}")
        
        BackupLog.objects.create(
            instance=instance,
            job=instance.job,
            level='error',
            step='failed',
            message=f'Backup {instance.id} falló: {instance.error_message}',
            timestamp=timezone.now()
        )


@receiver(post_save, sender=RestoreJob)
def restore_job_post_save(sender, instance, created, **kwargs):
    """Señal post-save para RestoreJob"""
    if created:
        logger.info(f"Nuevo trabajo de restauración creado: {instance.id}")
        
        BackupLog.objects.create(
            instance=instance.backup_instance,
            job=instance.backup_instance.job,
            level='info',
            step='restore_created',
            message=f'Trabajo de restauración {instance.id} creado',
            timestamp=timezone.now()
        )
    
    # Si se completó la restauración
    if not created and instance.status == 'completed':
        logger.info(f"Restauración completada: {instance.id}")
        
        BackupLog.objects.create(
            instance=instance.backup_instance,
            job=instance.backup_instance.job,
            level='info',
            step='restore_completed',
            message=f'Restauración {instance.id} completada exitosamente',
            timestamp=timezone.now()
        )
    
    # Si falló la restauración
    elif not created and instance.status == 'failed':
        logger.error(f"Restauración falló: {instance.id} - {instance.error_message}")
        
        BackupLog.objects.create(
            instance=instance.backup_instance,
            job=instance.backup_instance.job,
            level='error',
            step='restore_failed',
            message=f'Restauración {instance.id} falló: {instance.error_message}',
            timestamp=timezone.now()
        )


@receiver(post_save, sender=BackupSchedule)
def backup_schedule_post_save(sender, instance, created, **kwargs):
    """Señal post-save para BackupSchedule"""
    if created:
        logger.info(f"Nueva programación creada: {instance.name}")
        
        # Si está activa, programar próxima ejecución
        if instance.status == 'active':
            _schedule_next_execution(instance)
    
    # Si se reactivó la programación
    if not created and instance.status == 'active':
        logger.info(f"Programación reactivada: {instance.name}")
        _schedule_next_execution(instance)


@receiver(post_save, sender=BackupStorage)
def backup_storage_post_save(sender, instance, created, **kwargs):
    """Señal post-save para BackupStorage"""
    if created:
        logger.info(f"Nuevo almacenamiento creado: {instance.name}")
    
    # Si se desactivó el almacenamiento, pausar trabajos que lo usan
    if not created and not instance.is_active:
        jobs = BackupJob.objects.filter(storage=instance, status='active')
        for job in jobs:
            job.status = 'paused'
            job.save()
            logger.warning(f"Trabajo de backup pausado por almacenamiento inactivo: {job.name}")


@receiver(post_save, sender=BackupPolicy)
def backup_policy_post_save(sender, instance, created, **kwargs):
    """Señal post-save para BackupPolicy"""
    if created:
        logger.info(f"Nueva política creada: {instance.name}")
    
    # Si se activó la política, aplicarla a trabajos existentes
    if not created and instance.is_active:
        _apply_policy_to_jobs(instance)


@receiver(post_delete, sender=BackupJob)
def backup_job_post_delete(sender, instance, **kwargs):
    """Señal post-delete para BackupJob"""
    logger.info(f"Trabajo de backup eliminado: {instance.name}")
    
    # Eliminar programaciones asociadas
    schedules = BackupSchedule.objects.filter(job=instance)
    for schedule in schedules:
        schedule.delete()
        logger.info(f"Programación eliminada: {schedule.name}")


@receiver(post_delete, sender=BackupInstance)
def backup_instance_post_delete(sender, instance, **kwargs):
    """Señal post-delete para BackupInstance"""
    logger.info(f"Instancia de backup eliminada: {instance.id}")
    
    # Eliminar archivo de backup si existe
    if instance.backup_path and os.path.exists(instance.backup_path):
        try:
            os.remove(instance.backup_path)
            logger.info(f"Archivo de backup eliminado: {instance.backup_path}")
        except Exception as e:
            logger.error(f"Error eliminando archivo de backup: {str(e)}")


@receiver(post_delete, sender=BackupSchedule)
def backup_schedule_post_delete(sender, instance, **kwargs):
    """Señal post-delete para BackupSchedule"""
    logger.info(f"Programación eliminada: {instance.name}")


@receiver(post_delete, sender=BackupStorage)
def backup_storage_post_delete(sender, instance, **kwargs):
    """Señal post-delete para BackupStorage"""
    logger.info(f"Almacenamiento eliminado: {instance.name}")
    
    # Pausar trabajos que usan este almacenamiento
    jobs = BackupJob.objects.filter(storage=instance)
    for job in jobs:
        job.status = 'paused'
        job.save()
        logger.warning(f"Trabajo de backup pausado por eliminación de almacenamiento: {job.name}")


@receiver(post_delete, sender=BackupPolicy)
def backup_policy_post_delete(sender, instance, **kwargs):
    """Señal post-delete para BackupPolicy"""
    logger.info(f"Política eliminada: {instance.name}")


def _apply_retention_policies(job):
    """Aplicar políticas de retención a un trabajo de backup"""
    try:
        # Obtener políticas activas para este tipo de backup
        policies = BackupPolicy.objects.filter(
            is_active=True,
            backup_types__contains=[job.backup_type]
        ).order_by('priority')
        
        for policy in policies:
            if policy.policy_type == 'retention':
                _apply_retention_policy(job, policy)
            elif policy.policy_type == 'compression':
                _apply_compression_policy(job, policy)
            elif policy.policy_type == 'encryption':
                _apply_encryption_policy(job, policy)
                
    except Exception as e:
        logger.error(f"Error aplicando políticas de retención: {str(e)}")


def _apply_retention_policy(job, policy):
    """Aplicar política de retención"""
    try:
        retention_days = policy.config.get('retention_days', 30)
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Eliminar instancias antiguas
        old_instances = BackupInstance.objects.filter(
            job=job,
            status='completed',
            started_at__lt=cutoff_date
        )
        
        for instance in old_instances:
            # Eliminar archivo de backup
            if instance.backup_path and os.path.exists(instance.backup_path):
                os.remove(instance.backup_path)
            
            # Eliminar instancia
            instance.delete()
            logger.info(f"Instancia de backup eliminada por política de retención: {instance.id}")
            
    except Exception as e:
        logger.error(f"Error aplicando política de retención: {str(e)}")


def _apply_compression_policy(job, policy):
    """Aplicar política de compresión"""
    try:
        compression_level = policy.config.get('compression_level', 6)
        
        # Aplicar compresión a instancias recientes
        recent_instances = BackupInstance.objects.filter(
            job=job,
            status='completed',
            started_at__gte=timezone.now() - timedelta(days=1)
        )
        
        for instance in recent_instances:
            if instance.backup_path and os.path.exists(instance.backup_path):
                # Comprimir archivo
                compressed_path = f"{instance.backup_path}.gz"
                with open(instance.backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Reemplazar archivo original
                os.remove(instance.backup_path)
                os.rename(compressed_path, instance.backup_path)
                
                logger.info(f"Archivo de backup comprimido: {instance.backup_path}")
                
    except Exception as e:
        logger.error(f"Error aplicando política de compresión: {str(e)}")


def _apply_encryption_policy(job, policy):
    """Aplicar política de encriptación"""
    try:
        encryption_key = policy.config.get('encryption_key')
        if not encryption_key:
            logger.warning("Clave de encriptación no configurada")
            return
        
        # Aplicar encriptación a instancias recientes
        recent_instances = BackupInstance.objects.filter(
            job=job,
            status='completed',
            started_at__gte=timezone.now() - timedelta(days=1)
        )
        
        for instance in recent_instances:
            if instance.backup_path and os.path.exists(instance.backup_path):
                # Encriptar archivo
                from cryptography.fernet import Fernet
                
                f = Fernet(encryption_key.encode())
                
                with open(instance.backup_path, 'rb') as f_in:
                    encrypted_data = f.encrypt(f_in.read())
                
                with open(instance.backup_path, 'wb') as f_out:
                    f_out.write(encrypted_data)
                
                logger.info(f"Archivo de backup encriptado: {instance.backup_path}")
                
    except Exception as e:
        logger.error(f"Error aplicando política de encriptación: {str(e)}")


def _schedule_next_execution(schedule):
    """Programar próxima ejecución de una programación"""
    try:
        from celery import shared_task
        
        # Calcular próxima ejecución
        next_execution = _calculate_next_execution(schedule)
        
        if next_execution:
            # Programar tarea
            execute_backup_schedule.apply_async(
                args=[schedule.id],
                eta=next_execution
            )
            logger.info(f"Próxima ejecución programada para: {next_execution}")
            
    except Exception as e:
        logger.error(f"Error programando próxima ejecución: {str(e)}")


def _calculate_next_execution(schedule):
    """Calcular próxima ejecución basada en la configuración"""
    try:
        now = timezone.now()
        schedule_type = schedule.schedule_type
        config = schedule.schedule_config or {}
        
        if schedule_type == 'daily':
            # Ejecutar diariamente a la hora especificada
            hour = config.get('hour', 2)
            minute = config.get('minute', 0)
            
            next_execution = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_execution <= now:
                next_execution += timedelta(days=1)
            
            return next_execution
            
        elif schedule_type == 'weekly':
            # Ejecutar semanalmente
            weekday = config.get('weekday', 0)  # 0 = Lunes
            hour = config.get('hour', 2)
            minute = config.get('minute', 0)
            
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            
            next_execution = now + timedelta(days=days_ahead)
            next_execution = next_execution.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_execution
            
        elif schedule_type == 'monthly':
            # Ejecutar mensualmente
            day = config.get('day', 1)
            hour = config.get('hour', 2)
            minute = config.get('minute', 0)
            
            # Calcular próximo mes
            if now.day >= day:
                # Próximo mes
                if now.month == 12:
                    next_execution = now.replace(year=now.year + 1, month=1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    next_execution = now.replace(month=now.month + 1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # Este mes
                next_execution = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_execution
            
        elif schedule_type == 'interval':
            # Ejecutar en intervalos
            interval_minutes = config.get('interval_minutes', 60)
            next_execution = now + timedelta(minutes=interval_minutes)
            
            return next_execution
        
        return None
        
    except Exception as e:
        logger.error(f"Error calculando próxima ejecución: {str(e)}")
        return None


def _apply_policy_to_jobs(policy):
    """Aplicar política a trabajos existentes"""
    try:
        # Obtener trabajos que coinciden con la política
        jobs = BackupJob.objects.filter(
            backup_type__in=policy.backup_types,
            status='active'
        )
        
        for job in jobs:
            # Aplicar política
            if policy.policy_type == 'retention':
                _apply_retention_policy(job, policy)
            elif policy.policy_type == 'compression':
                _apply_compression_policy(job, policy)
            elif policy.policy_type == 'encryption':
                _apply_encryption_policy(job, policy)
                
        logger.info(f"Política {policy.name} aplicada a {jobs.count()} trabajos")
        
    except Exception as e:
        logger.error(f"Error aplicando política a trabajos: {str(e)}")


# Tarea de Celery para ejecutar programaciones
@shared_task
def execute_backup_schedule(schedule_id):
    """Ejecutar programación de backup"""
    try:
        schedule = BackupSchedule.objects.get(id=schedule_id)
        
        if schedule.status != 'active':
            logger.warning(f"Programación no activa: {schedule.name}")
            return
        
        # Ejecutar backup
        from .services import BackupService
        service = BackupService()
        instance = service.execute_backup(schedule.job, schedule.options or {}, schedule.created_by)
        
        logger.info(f"Programación ejecutada exitosamente: {schedule.name}")
        
        # Programar próxima ejecución
        _schedule_next_execution(schedule)
        
        return instance.id
        
    except Exception as e:
        logger.error(f"Error ejecutando programación {schedule_id}: {str(e)}")
        raise
