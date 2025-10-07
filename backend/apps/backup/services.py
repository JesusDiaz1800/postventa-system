import os
import zipfile
import shutil
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
import subprocess
import json

from .models import (
    BackupJob, BackupInstance, RestoreJob, BackupSchedule, 
    BackupStorage, BackupLog, BackupPolicy
)

logger = logging.getLogger(__name__)


class BackupService:
    """Servicio para operaciones de backup"""
    
    def __init__(self):
        self.backup_dir = getattr(settings, 'BACKUP_DIR', '/tmp/backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def execute_backup(self, job, options, user):
        """Ejecutar trabajo de backup"""
        try:
            # Crear instancia de backup
            instance = BackupInstance.objects.create(
                job=job,
                status='running',
                started_by=user,
                started_at=timezone.now(),
                options=options
            )
            
            # Log de inicio
            self._log_backup(instance, 'info', 'Iniciando backup', 'start')
            
            # Ejecutar backup según el tipo
            if job.backup_type == 'full':
                result = self._execute_full_backup(instance, options)
            elif job.backup_type == 'incremental':
                result = self._execute_incremental_backup(instance, options)
            elif job.backup_type == 'differential':
                result = self._execute_differential_backup(instance, options)
            else:
                raise ValueError(f"Tipo de backup no soportado: {job.backup_type}")
            
            # Actualizar instancia
            instance.status = 'completed'
            instance.completed_at = timezone.now()
            instance.backup_path = result.get('backup_path')
            instance.backup_size = result.get('backup_size', 0)
            instance.duration = (instance.completed_at - instance.started_at).total_seconds()
            instance.save()
            
            # Log de finalización
            self._log_backup(instance, 'info', 'Backup completado exitosamente', 'complete')
            
            return instance
            
        except Exception as e:
            logger.error(f"Error executing backup job {job.name}: {str(e)}")
            
            # Actualizar instancia con error
            if 'instance' in locals():
                instance.status = 'failed'
                instance.completed_at = timezone.now()
                instance.duration = (instance.completed_at - instance.started_at).total_seconds()
                instance.error_message = str(e)
                instance.save()
                
                self._log_backup(instance, 'error', f'Error en backup: {str(e)}', 'error')
            
            raise
    
    def _execute_full_backup(self, instance, options):
        """Ejecutar backup completo"""
        backup_name = f"full_backup_{instance.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        
        # Crear archivo ZIP
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup de base de datos
            if 'include_database' in options and options['include_database']:
                self._backup_database(zipf, instance)
            
            # Backup de archivos
            if 'include_files' in options and options['include_files']:
                self._backup_files(zipf, instance, options.get('file_paths', []))
            
            # Backup de configuración
            if 'include_config' in options and options['include_config']:
                self._backup_config(zipf, instance)
        
        # Obtener tamaño del archivo
        backup_size = os.path.getsize(backup_path)
        
        return {
            'backup_path': backup_path,
            'backup_size': backup_size
        }
    
    def _execute_incremental_backup(self, instance, options):
        """Ejecutar backup incremental"""
        # Obtener último backup completo
        last_full = BackupInstance.objects.filter(
            job=instance.job,
            status='completed'
        ).exclude(id=instance.id).order_by('-started_at').first()
        
        if not last_full:
            # Si no hay backup completo previo, hacer backup completo
            return self._execute_full_backup(instance, options)
        
        backup_name = f"incremental_backup_{instance.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        
        # Crear archivo ZIP
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup incremental de archivos modificados desde el último backup
            self._backup_incremental_files(zipf, instance, last_full.started_at, options.get('file_paths', []))
        
        # Obtener tamaño del archivo
        backup_size = os.path.getsize(backup_path)
        
        return {
            'backup_path': backup_path,
            'backup_size': backup_size
        }
    
    def _execute_differential_backup(self, instance, options):
        """Ejecutar backup diferencial"""
        # Obtener último backup completo
        last_full = BackupInstance.objects.filter(
            job=instance.job,
            status='completed'
        ).exclude(id=instance.id).order_by('-started_at').first()
        
        if not last_full:
            # Si no hay backup completo previo, hacer backup completo
            return self._execute_full_backup(instance, options)
        
        backup_name = f"differential_backup_{instance.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        
        # Crear archivo ZIP
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup diferencial de archivos modificados desde el último backup completo
            self._backup_differential_files(zipf, instance, last_full.started_at, options.get('file_paths', []))
        
        # Obtener tamaño del archivo
        backup_size = os.path.getsize(backup_path)
        
        return {
            'backup_path': backup_path,
            'backup_size': backup_size
        }
    
    def _backup_database(self, zipf, instance):
        """Backup de base de datos"""
        try:
            # Obtener configuración de base de datos
            db_config = settings.DATABASES['default']
            
            if db_config['ENGINE'] == 'django.db.backends.postgresql':
                # Backup de PostgreSQL
                db_name = db_config['NAME']
                db_user = db_config['USER']
                db_host = db_config.get('HOST', 'localhost')
                db_port = db_config.get('PORT', '5432')
                
                dump_file = f"database_dump_{instance.id}.sql"
                dump_path = os.path.join(self.backup_dir, dump_file)
                
                # Ejecutar pg_dump
                cmd = [
                    'pg_dump',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-d', db_name,
                    '-f', dump_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Agregar al ZIP
                zipf.write(dump_path, f"database/{dump_file}")
                
                # Limpiar archivo temporal
                os.remove(dump_path)
                
            elif db_config['ENGINE'] == 'django.db.backends.mysql':
                # Backup de MySQL
                db_name = db_config['NAME']
                db_user = db_config['USER']
                db_host = db_config.get('HOST', 'localhost')
                db_port = db_config.get('PORT', '3306')
                
                dump_file = f"database_dump_{instance.id}.sql"
                dump_path = os.path.join(self.backup_dir, dump_file)
                
                # Ejecutar mysqldump
                cmd = [
                    'mysqldump',
                    '-h', db_host,
                    '-P', str(db_port),
                    '-u', db_user,
                    '-p' + db_config.get('PASSWORD', ''),
                    db_name
                ]
                
                with open(dump_path, 'w') as f:
                    subprocess.run(cmd, check=True, stdout=f, capture_output=True)
                
                # Agregar al ZIP
                zipf.write(dump_path, f"database/{dump_file}")
                
                # Limpiar archivo temporal
                os.remove(dump_path)
            
            self._log_backup(instance, 'info', 'Backup de base de datos completado', 'database_backup')
            
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            self._log_backup(instance, 'error', f'Error en backup de base de datos: {str(e)}', 'database_backup')
            raise
    
    def _backup_files(self, zipf, instance, file_paths):
        """Backup de archivos"""
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        zipf.write(file_path, f"files/{os.path.basename(file_path)}")
                    elif os.path.isdir(file_path):
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                file_full_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_full_path, file_path)
                                zipf.write(file_full_path, f"files/{arcname}")
            
            self._log_backup(instance, 'info', 'Backup de archivos completado', 'files_backup')
            
        except Exception as e:
            logger.error(f"Error backing up files: {str(e)}")
            self._log_backup(instance, 'error', f'Error en backup de archivos: {str(e)}', 'files_backup')
            raise
    
    def _backup_incremental_files(self, zipf, instance, since_date, file_paths):
        """Backup incremental de archivos"""
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        if os.path.getmtime(file_path) > since_date.timestamp():
                            zipf.write(file_path, f"files/{os.path.basename(file_path)}")
                    elif os.path.isdir(file_path):
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                file_full_path = os.path.join(root, file)
                                if os.path.getmtime(file_full_path) > since_date.timestamp():
                                    arcname = os.path.relpath(file_full_path, file_path)
                                    zipf.write(file_full_path, f"files/{arcname}")
            
            self._log_backup(instance, 'info', 'Backup incremental de archivos completado', 'incremental_files_backup')
            
        except Exception as e:
            logger.error(f"Error backing up incremental files: {str(e)}")
            self._log_backup(instance, 'error', f'Error en backup incremental de archivos: {str(e)}', 'incremental_files_backup')
            raise
    
    def _backup_differential_files(self, zipf, instance, since_date, file_paths):
        """Backup diferencial de archivos"""
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        if os.path.getmtime(file_path) > since_date.timestamp():
                            zipf.write(file_path, f"files/{os.path.basename(file_path)}")
                    elif os.path.isdir(file_path):
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                file_full_path = os.path.join(root, file)
                                if os.path.getmtime(file_full_path) > since_date.timestamp():
                                    arcname = os.path.relpath(file_full_path, file_path)
                                    zipf.write(file_full_path, f"files/{arcname}")
            
            self._log_backup(instance, 'info', 'Backup diferencial de archivos completado', 'differential_files_backup')
            
        except Exception as e:
            logger.error(f"Error backing up differential files: {str(e)}")
            self._log_backup(instance, 'error', f'Error en backup diferencial de archivos: {str(e)}', 'differential_files_backup')
            raise
    
    def _backup_config(self, zipf, instance):
        """Backup de configuración"""
        try:
            # Backup de settings.py
            settings_path = os.path.join(settings.BASE_DIR, 'postventa_system', 'settings.py')
            if os.path.exists(settings_path):
                zipf.write(settings_path, 'config/settings.py')
            
            # Backup de requirements.txt
            requirements_path = os.path.join(settings.BASE_DIR, 'requirements.txt')
            if os.path.exists(requirements_path):
                zipf.write(requirements_path, 'config/requirements.txt')
            
            # Backup de configuración de Django
            config_data = {
                'installed_apps': settings.INSTALLED_APPS,
                'middleware': settings.MIDDLEWARE,
                'databases': {
                    'default': {
                        'engine': settings.DATABASES['default']['ENGINE'],
                        'name': settings.DATABASES['default']['NAME'],
                    }
                }
            }
            
            config_json = json.dumps(config_data, indent=2)
            zipf.writestr('config/django_config.json', config_json)
            
            self._log_backup(instance, 'info', 'Backup de configuración completado', 'config_backup')
            
        except Exception as e:
            logger.error(f"Error backing up config: {str(e)}")
            self._log_backup(instance, 'error', f'Error en backup de configuración: {str(e)}', 'config_backup')
            raise
    
    def test_backup(self, job, options):
        """Probar trabajo de backup"""
        try:
            # Crear instancia de prueba
            test_instance = BackupInstance.objects.create(
                job=job,
                status='testing',
                started_at=timezone.now(),
                options=options
            )
            
            # Ejecutar backup de prueba
            if job.backup_type == 'full':
                result = self._execute_full_backup(test_instance, options)
            elif job.backup_type == 'incremental':
                result = self._execute_incremental_backup(test_instance, options)
            elif job.backup_type == 'differential':
                result = self._execute_differential_backup(test_instance, options)
            else:
                raise ValueError(f"Tipo de backup no soportado: {job.backup_type}")
            
            # Verificar integridad
            verification_result = self.verify_backup(test_instance)
            
            # Limpiar archivo de prueba
            if os.path.exists(result['backup_path']):
                os.remove(result['backup_path'])
            
            # Eliminar instancia de prueba
            test_instance.delete()
            
            return {
                'success': True,
                'backup_size': result['backup_size'],
                'verification': verification_result
            }
            
        except Exception as e:
            logger.error(f"Error testing backup job {job.name}: {str(e)}")
            raise
    
    def verify_backup(self, instance):
        """Verificar integridad del backup"""
        try:
            if not instance.backup_path or not os.path.exists(instance.backup_path):
                return {
                    'success': False,
                    'message': 'Archivo de backup no encontrado'
                }
            
            # Verificar archivo ZIP
            with zipfile.ZipFile(instance.backup_path, 'r') as zipf:
                # Verificar integridad del ZIP
                bad_file = zipf.testzip()
                if bad_file:
                    return {
                        'success': False,
                        'message': f'Archivo corrupto en backup: {bad_file}'
                    }
                
                # Obtener información del contenido
                file_list = zipf.namelist()
                total_files = len(file_list)
                total_size = sum(info.file_size for info in zipf.infolist())
                
                return {
                    'success': True,
                    'message': 'Backup verificado exitosamente',
                    'total_files': total_files,
                    'total_size': total_size,
                    'file_list': file_list
                }
                
        except Exception as e:
            logger.error(f"Error verifying backup {instance.id}: {str(e)}")
            return {
                'success': False,
                'message': f'Error verificando backup: {str(e)}'
            }
    
    def cancel_backup(self, job, user):
        """Cancelar trabajo de backup"""
        try:
            # Buscar instancias en ejecución
            running_instances = BackupInstance.objects.filter(
                job=job,
                status='running'
            )
            
            for instance in running_instances:
                instance.status = 'cancelled'
                instance.completed_at = timezone.now()
                instance.duration = (instance.completed_at - instance.started_at).total_seconds()
                instance.save()
                
                self._log_backup(instance, 'warning', 'Backup cancelado por usuario', 'cancel')
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling backup job {job.id}: {str(e)}")
            raise
    
    def execute_schedule(self, schedule, user):
        """Ejecutar programación de backup"""
        try:
            # Crear instancia de backup
            instance = BackupInstance.objects.create(
                job=schedule.job,
                status='running',
                started_by=user,
                started_at=timezone.now(),
                options=schedule.options or {}
            )
            
            # Ejecutar backup
            result = self.execute_backup(schedule.job, schedule.options or {}, user)
            
            # Actualizar última ejecución
            schedule.last_execution = timezone.now()
            schedule.save()
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing schedule {schedule.id}: {str(e)}")
            raise
    
    def _log_backup(self, instance, level, message, step):
        """Registrar log de backup"""
        BackupLog.objects.create(
            instance=instance,
            job=instance.job,
            level=level,
            step=step,
            message=message,
            timestamp=timezone.now()
        )


class RestoreService:
    """Servicio para operaciones de restauración"""
    
    def __init__(self):
        self.restore_dir = getattr(settings, 'RESTORE_DIR', '/tmp/restores')
        os.makedirs(self.restore_dir, exist_ok=True)
    
    def execute_restore(self, restore_job, options, user):
        """Ejecutar trabajo de restauración"""
        try:
            # Actualizar estado
            restore_job.status = 'running'
            restore_job.started_at = timezone.now()
            restore_job.started_by = user
            restore_job.save()
            
            # Log de inicio
            self._log_restore(restore_job, 'info', 'Iniciando restauración', 'start')
            
            # Verificar backup
            if not os.path.exists(restore_job.backup_instance.backup_path):
                raise FileNotFoundError("Archivo de backup no encontrado")
            
            # Ejecutar restauración
            result = self._execute_restore(restore_job, options)
            
            # Actualizar estado
            restore_job.status = 'completed'
            restore_job.completed_at = timezone.now()
            restore_job.duration = (restore_job.completed_at - restore_job.started_at).total_seconds()
            restore_job.save()
            
            # Log de finalización
            self._log_restore(restore_job, 'info', 'Restauración completada exitosamente', 'complete')
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing restore job {restore_job.id}: {str(e)}")
            
            # Actualizar estado con error
            restore_job.status = 'failed'
            restore_job.completed_at = timezone.now()
            restore_job.duration = (restore_job.completed_at - restore_job.started_at).total_seconds()
            restore_job.error_message = str(e)
            restore_job.save()
            
            self._log_restore(restore_job, 'error', f'Error en restauración: {str(e)}', 'error')
            
            raise
    
    def _execute_restore(self, restore_job, options):
        """Ejecutar restauración"""
        backup_path = restore_job.backup_instance.backup_path
        
        # Crear directorio de restauración
        restore_path = os.path.join(self.restore_dir, f"restore_{restore_job.id}")
        os.makedirs(restore_path, exist_ok=True)
        
        try:
            # Extraer archivo ZIP
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)
            
            # Restaurar base de datos
            if 'restore_database' in options and options['restore_database']:
                self._restore_database(restore_job, restore_path, options)
            
            # Restaurar archivos
            if 'restore_files' in options and options['restore_files']:
                self._restore_files(restore_job, restore_path, options)
            
            # Restaurar configuración
            if 'restore_config' in options and options['restore_config']:
                self._restore_config(restore_job, restore_path, options)
            
            return {
                'success': True,
                'restore_path': restore_path
            }
            
        finally:
            # Limpiar directorio temporal
            if os.path.exists(restore_path):
                shutil.rmtree(restore_path)
    
    def _restore_database(self, restore_job, restore_path, options):
        """Restaurar base de datos"""
        try:
            # Buscar archivo de dump
            database_dir = os.path.join(restore_path, 'database')
            if not os.path.exists(database_dir):
                return
            
            dump_files = [f for f in os.listdir(database_dir) if f.endswith('.sql')]
            if not dump_files:
                return
            
            dump_file = os.path.join(database_dir, dump_files[0])
            
            # Obtener configuración de base de datos
            db_config = settings.DATABASES['default']
            
            if db_config['ENGINE'] == 'django.db.backends.postgresql':
                # Restaurar PostgreSQL
                db_name = db_config['NAME']
                db_user = db_config['USER']
                db_host = db_config.get('HOST', 'localhost')
                db_port = db_config.get('PORT', '5432')
                
                cmd = [
                    'psql',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-d', db_name,
                    '-f', dump_file
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
            elif db_config['ENGINE'] == 'django.db.backends.mysql':
                # Restaurar MySQL
                db_name = db_config['NAME']
                db_user = db_config['USER']
                db_host = db_config.get('HOST', 'localhost')
                db_port = db_config.get('PORT', '3306')
                
                cmd = [
                    'mysql',
                    '-h', db_host,
                    '-P', str(db_port),
                    '-u', db_user,
                    '-p' + db_config.get('PASSWORD', ''),
                    db_name
                ]
                
                with open(dump_file, 'r') as f:
                    subprocess.run(cmd, check=True, stdin=f, capture_output=True)
            
            self._log_restore(restore_job, 'info', 'Restauración de base de datos completada', 'database_restore')
            
        except Exception as e:
            logger.error(f"Error restoring database: {str(e)}")
            self._log_restore(restore_job, 'error', f'Error en restauración de base de datos: {str(e)}', 'database_restore')
            raise
    
    def _restore_files(self, restore_job, restore_path, options):
        """Restaurar archivos"""
        try:
            files_dir = os.path.join(restore_path, 'files')
            if not os.path.exists(files_dir):
                return
            
            # Obtener rutas de destino
            target_paths = options.get('target_paths', [])
            if not target_paths:
                # Usar rutas por defecto
                target_paths = [settings.MEDIA_ROOT, settings.STATIC_ROOT]
            
            for target_path in target_paths:
                if os.path.exists(target_path):
                    # Copiar archivos
                    for root, dirs, files in os.walk(files_dir):
                        for file in files:
                            src_file = os.path.join(root, file)
                            rel_path = os.path.relpath(src_file, files_dir)
                            dst_file = os.path.join(target_path, rel_path)
                            
                            # Crear directorio de destino si no existe
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            
                            # Copiar archivo
                            shutil.copy2(src_file, dst_file)
            
            self._log_restore(restore_job, 'info', 'Restauración de archivos completada', 'files_restore')
            
        except Exception as e:
            logger.error(f"Error restoring files: {str(e)}")
            self._log_restore(restore_job, 'error', f'Error en restauración de archivos: {str(e)}', 'files_restore')
            raise
    
    def _restore_config(self, restore_job, restore_path, options):
        """Restaurar configuración"""
        try:
            config_dir = os.path.join(restore_path, 'config')
            if not os.path.exists(config_dir):
                return
            
            # Restaurar archivos de configuración
            config_files = os.listdir(config_dir)
            for config_file in config_files:
                src_file = os.path.join(config_dir, config_file)
                if config_file == 'settings.py':
                    # Backup del archivo actual
                    current_settings = os.path.join(settings.BASE_DIR, 'postventa_system', 'settings.py')
                    if os.path.exists(current_settings):
                        backup_settings = f"{current_settings}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(current_settings, backup_settings)
                    
                    # Copiar nuevo archivo
                    shutil.copy2(src_file, current_settings)
            
            self._log_restore(restore_job, 'info', 'Restauración de configuración completada', 'config_restore')
            
        except Exception as e:
            logger.error(f"Error restoring config: {str(e)}")
            self._log_restore(restore_job, 'error', f'Error en restauración de configuración: {str(e)}', 'config_restore')
            raise
    
    def cancel_restore(self, restore_job, user):
        """Cancelar trabajo de restauración"""
        try:
            restore_job.status = 'cancelled'
            restore_job.completed_at = timezone.now()
            restore_job.duration = (restore_job.completed_at - restore_job.started_at).total_seconds()
            restore_job.save()
            
            self._log_restore(restore_job, 'warning', 'Restauración cancelada por usuario', 'cancel')
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling restore job {restore_job.id}: {str(e)}")
            raise
    
    def _log_restore(self, restore_job, level, message, step):
        """Registrar log de restauración"""
        BackupLog.objects.create(
            instance=restore_job.backup_instance,
            job=restore_job.backup_instance.job,
            level=level,
            step=f"restore_{step}",
            message=message,
            timestamp=timezone.now()
        )


class StorageService:
    """Servicio para operaciones de almacenamiento"""
    
    def test_storage(self, storage, options):
        """Probar almacenamiento"""
        try:
            if storage.storage_type == 'local':
                return self._test_local_storage(storage, options)
            elif storage.storage_type == 's3':
                return self._test_s3_storage(storage, options)
            elif storage.storage_type == 'ftp':
                return self._test_ftp_storage(storage, options)
            else:
                raise ValueError(f"Tipo de almacenamiento no soportado: {storage.storage_type}")
                
        except Exception as e:
            logger.error(f"Error testing storage {storage.name}: {str(e)}")
            raise
    
    def _test_local_storage(self, storage, options):
        """Probar almacenamiento local"""
        try:
            # Verificar que el directorio existe y es accesible
            if not os.path.exists(storage.config.get('path', '')):
                raise FileNotFoundError("Directorio de almacenamiento no encontrado")
            
            # Crear archivo de prueba
            test_file = os.path.join(storage.config.get('path', ''), 'test_backup.txt')
            with open(test_file, 'w') as f:
                f.write('Test backup file')
            
            # Verificar que se puede leer
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Limpiar archivo de prueba
            os.remove(test_file)
            
            return {
                'success': True,
                'message': 'Almacenamiento local verificado exitosamente',
                'path': storage.config.get('path', ''),
                'writable': True,
                'readable': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error verificando almacenamiento local: {str(e)}',
                'error': str(e)
            }
    
    def _test_s3_storage(self, storage, options):
        """Probar almacenamiento S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Crear cliente S3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=storage.config.get('access_key'),
                aws_secret_access_key=storage.config.get('secret_key'),
                region_name=storage.config.get('region', 'us-east-1')
            )
            
            bucket_name = storage.config.get('bucket_name')
            
            # Verificar que el bucket existe
            try:
                s3_client.head_bucket(Bucket=bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise ValueError(f"Bucket {bucket_name} no encontrado")
                else:
                    raise
            
            # Crear archivo de prueba
            test_key = 'test_backup.txt'
            test_content = 'Test backup file'
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content
            )
            
            # Verificar que se puede leer
            response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
            content = response['Body'].read().decode('utf-8')
            
            # Limpiar archivo de prueba
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            
            return {
                'success': True,
                'message': 'Almacenamiento S3 verificado exitosamente',
                'bucket': bucket_name,
                'writable': True,
                'readable': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error verificando almacenamiento S3: {str(e)}',
                'error': str(e)
            }
    
    def _test_ftp_storage(self, storage, options):
        """Probar almacenamiento FTP"""
        try:
            import ftplib
            
            # Conectar al servidor FTP
            ftp = ftplib.FTP()
            ftp.connect(
                storage.config.get('host', 'localhost'),
                storage.config.get('port', 21)
            )
            ftp.login(
                storage.config.get('username', ''),
                storage.config.get('password', '')
            )
            
            # Cambiar al directorio de destino
            ftp.cwd(storage.config.get('path', '/'))
            
            # Crear archivo de prueba
            test_content = 'Test backup file'
            test_filename = 'test_backup.txt'
            
            ftp.storbinary(f'STOR {test_filename}', io.BytesIO(test_content.encode()))
            
            # Verificar que se puede leer
            ftp.retrbinary(f'RETR {test_filename}', lambda data: data)
            
            # Limpiar archivo de prueba
            ftp.delete(test_filename)
            
            # Cerrar conexión
            ftp.quit()
            
            return {
                'success': True,
                'message': 'Almacenamiento FTP verificado exitosamente',
                'host': storage.config.get('host', 'localhost'),
                'path': storage.config.get('path', '/'),
                'writable': True,
                'readable': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error verificando almacenamiento FTP: {str(e)}',
                'error': str(e)
            }
