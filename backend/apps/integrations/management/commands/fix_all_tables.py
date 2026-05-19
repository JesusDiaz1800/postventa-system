"""
Django management command to fix ALL missing database tables
Uses Django's schema editor to create missing tables
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create all missing database tables for Django models'

    def handle(self, *args, **options):
        self.stdout.write('Checking for missing database tables...\n')
        
        # Get all Django models
        all_models = apps.get_models()
        
        # Get existing tables from SQL Server
        existing_tables = set()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            for row in cursor.fetchall():
                existing_tables.add(row[0].lower())
        
        self.stdout.write(f'Found {len(existing_tables)} existing tables in database\n')
        
        # Find missing tables
        missing_models = []
        for model in all_models:
            table_name = model._meta.db_table
            if table_name.lower() not in existing_tables:
                missing_models.append(model)
                self.stdout.write(self.style.WARNING(f'  [MISSING] {table_name}'))
        
        if not missing_models:
            self.stdout.write(self.style.SUCCESS('\n[OK] All tables exist in database!'))
            return
        
        self.stdout.write(f'\n{len(missing_models)} tables are missing. Creating them...\n')
        
        # Create missing tables using Django's schema editor
        created_count = 0
        error_count = 0
        
        with connection.schema_editor() as schema_editor:
            for model in missing_models:
                try:
                    self.stdout.write(f'  Creating table: {model._meta.db_table}...')
                    schema_editor.create_model(model)
                    self.stdout.write(self.style.SUCCESS(' [OK]'))
                    created_count += 1
                except Exception as e:
                    error_message = str(e)
                    if 'already exists' in error_message.lower():
                        self.stdout.write(self.style.WARNING(' [SKIPPED - already exists]'))
                    else:
                        self.stdout.write(self.style.ERROR(f' [ERROR: {error_message[:50]}]'))
                        error_count += 1
        
        self.stdout.write('')
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'[OK] Created {created_count} tables'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'[ERROR] {error_count} tables failed'))
        
        self.stdout.write(self.style.SUCCESS('\nDone! Restart Django server to apply changes.'))
