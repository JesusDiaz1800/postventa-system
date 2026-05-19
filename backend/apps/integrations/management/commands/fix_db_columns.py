"""
Django management command to fix missing columns in integrations tables
"""
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix missing columns in integrations tables (webhookendpoint)'

    def handle(self, *args, **options):
        self.stdout.write('Fixing missing columns in integrations tables...\n')
        
        columns_to_add = [
            ('description', "NVARCHAR(MAX) NULL"),
            ('url_path', "NVARCHAR(200) NOT NULL DEFAULT ''"),
            ('http_method', "NVARCHAR(10) NOT NULL DEFAULT 'POST'"),
            ('requires_auth', "BIT NOT NULL DEFAULT 1"),
            ('auth_token', "NVARCHAR(255) NULL"),
            ('validate_signature', "BIT NOT NULL DEFAULT 0"),
            ('signature_header', "NVARCHAR(100) NULL"),
            ('signature_secret', "NVARCHAR(255) NULL"),
            ('auto_process', "BIT NOT NULL DEFAULT 1"),
            ('processing_script', "NVARCHAR(MAX) NULL"),
            ('filter_conditions', "NVARCHAR(MAX) NULL"),
        ]
        
        added_count = 0
        
        with connection.cursor() as cursor:
            for column_name, column_def in columns_to_add:
                try:
                    # Check if column exists
                    cursor.execute("""
                        SELECT COUNT(*) FROM sys.columns 
                        WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') 
                        AND name = %s
                    """, [column_name])
                    result = cursor.fetchone()
                    
                    if result[0] == 0:
                        # Column doesn't exist, add it
                        sql = f"ALTER TABLE integrations_webhookendpoint ADD {column_name} {column_def}"
                        cursor.execute(sql)
                        self.stdout.write(self.style.SUCCESS(f'  [OK] Added column: {column_name}'))
                        added_count += 1
                    else:
                        self.stdout.write(f'  [-] Column already exists: {column_name}')
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  [ERROR] Error adding {column_name}: {str(e)}'))
        
        if added_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\n[OK] Added {added_count} missing columns'))
        else:
            self.stdout.write(self.style.WARNING('\n[-] No columns needed to be added'))
        
        self.stdout.write(self.style.SUCCESS('\nDone! Restart Django server to apply changes.'))
