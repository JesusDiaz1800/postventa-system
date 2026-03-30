import logging
from django.core.management.base import BaseCommand
from apps.users.models import User, RolePermission
from apps.users.permissions import ROLE_PERMISSIONS
from django.db import connections

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Inicializa los permisos de rol en la base de datos desde los valores por defecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            type=str,
            help='Base de datos específica para inicializar',
        )

    def handle(self, *args, **options):
        db_param = options.get('database')
        
        # Si se especifica una DB, usar solo esa. Si no, intentar con todas las conocidas.
        if db_param:
            target_dbs = [db_param]
        else:
            target_dbs = ['default', 'default_pe', 'default_co']

        for db in target_dbs:
            if db not in connections:
                self.stdout.write(self.style.WARNING(f"Base de datos '{db}' no configurada. Saltando..."))
                continue
            
            self.stdout.write(self.style.MIGRATE_HEADING(f"Iniciando inicialización en '{db}'..."))
            
            for role_code, role_name in User.ROLE_CHOICES:
                # Obtener permisos por defecto
                perms = ROLE_PERMISSIONS.get(role_code, {})
                
                # Definir páginas accesibles por defecto basándonos en la lógica de fallbacks
                pages = self.get_default_pages_for_role(role_code, perms)
                
                # Crear o actualizar
                role_perm, created = RolePermission.objects.using(db).update_or_create(
                    role=role_code,
                    defaults={
                        'permissions': perms,
                        'accessible_pages': pages
                    }
                )
                
                status = "creado" if created else "actualizado"
                self.stdout.write(f"  - Rol '{role_code}': {status}")
            
            self.stdout.write(self.style.SUCCESS(f"Finalizado con éxito en '{db}'"))

    def get_default_pages_for_role(self, role, perms):
        """Lógica de páginas por defecto simplificada para inicialización"""
        pages = ['reports', 'profile']
        
        if perms.get('can_manage_users'):
            pages.append('users')
        if perms.get('can_manage_incidents') or perms.get('can_view_reports'):
            pages.append('incidents')
        if perms.get('can_manage_documents'):
            pages.append('documents')
        if perms.get('can_view_audit_logs'):
            pages.append('audit')
        if perms.get('can_view_supplier_reports'):
            pages.append('supplier-reports')
            
        # Páginas adicionales por rol técnico/admin
        if role in ['admin', 'management', 'technical_service', 'quality', 'supervisor']:
            pages.extend(['visit-reports', 'quality-reports/client', 'quality-reports/internal'])
            
        if role in ['admin', 'management', 'supervisor', 'analyst']:
            pages.append('ai')
            
        return list(set(pages))
