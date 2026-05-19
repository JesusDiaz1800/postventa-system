import logging
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from apps.incidents.models import Incident, User
from django.utils import timezone
import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import historical service calls from SAP (OSCL table) as Incidents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of records to import (for testing)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without saving to database',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING("Starting SAP Historical Import..."))
        
        if 'sap_db' not in connections:
            self.stdout.write(self.style.ERROR("Error: 'sap_db' connection not defined in settings"))
            return

        # 1. Get or Create System User for Import
        system_user, _ = User.objects.get_or_create(
            email='sap_import@system.local',
            defaults={
                'first_name': 'SAP',
                'last_name': 'Histórico',
                'username': 'sap_import', # Ensure username field needs if exists
                'is_active': False
            }
        )
        if hasattr(system_user, 'set_unusable_password'):
            system_user.set_unusable_password()
            system_user.save()

        # 2. Build Query - CORRECTED: Use callType = 1 (Post-Vent) only
        # callType = 1 means "Post-Vent" (real incidents)
        # callType = 2 means "Visita Tecnica" (visits, NOT incidents) - e.g., ID 167
        
        # UDF Fields to extract
        udf_fields = ['U_NX_OBS_MATRIZ', 'U_NX_OBS_MURO', 'U_NX_OBS_LOSA', 'U_NX_OBS_ALMAC', 'U_NX_OBS_EXTER', 'descrption']
        udf_select = ", ".join(udf_fields)

        query = f"""
        SELECT callID, customer, custmrName, subject, createDate, status, 
               {udf_select}
        FROM OSCL 
        WHERE callType = 1
        ORDER BY createDate DESC
        """

        conn = connections['sap_db']
        cursor = conn.cursor()
        cursor.execute(query)
        
        columns = [col[0] for col in cursor.description]
        total_processed = 0
        total_created = 0
        total_skipped = 0
        
        batch_size = 500
        batch = []
        
        while True:
            if limit and total_processed >= limit:
                break
                
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
                
            for row in rows:
                total_processed += 1
                try:
                    data = dict(zip(columns, row))
                    
                    sap_id = data['callID']
                    
                    # Check duplication
                    if Incident.objects.filter(sap_call_id=sap_id).exists():
                        # self.stdout.write(f"Skipping existing SAP ID: {sap_id}")
                        total_skipped += 1
                        continue

                    # Construct Description
                    desc_parts = []
                    # Add Subject as header
                    desc_parts.append(f"Referencia SAP: {data['subject']}\n")
                    
                    # Add UDFs
                    if data.get('U_NX_OBS_MATRIZ'): desc_parts.append(f"[Obs. Matriz]: {data['U_NX_OBS_MATRIZ']}")
                    if data.get('U_NX_OBS_MURO'): desc_parts.append(f"[Obs. Muro]: {data['U_NX_OBS_MURO']}")
                    if data.get('U_NX_OBS_LOSA'): desc_parts.append(f"[Obs. Losa]: {data['U_NX_OBS_LOSA']}")
                    if data.get('U_NX_OBS_EXTER'): desc_parts.append(f"[Obs. Exter]: {data['U_NX_OBS_EXTER']}")
                    if data.get('descrption'): desc_parts.append(f"[Desc. Std]: {data['descrption']}")
                    
                    final_desc = "\n".join(desc_parts)
                    
                    # Dates
                    created_at = data['createDate']
                    if isinstance(created_at, datetime.datetime):
                         if timezone.is_naive(created_at):
                            created_at = make_aware(created_at)
                    else:
                        created_at = timezone.now() # Fallback

                    # Status Mapping
                    # SAP Status: -1 (Open), -3 (Closed) -> Default assumption
                    sap_status = data['status']
                    status_map = {
                        -3: 'cerrado', 
                        -1: 'abierto'
                    }
                    incident_status = status_map.get(sap_status, 'abierto')

                    incident = Incident(
                        code=f"SAP-{sap_id}",
                        sap_call_id=sap_id,
                        created_by=system_user,
                        cliente=data['custmrName'] or 'Sin Nombre',
                        customer_code=data['customer'] or 'N/A',
                        provider='SAP Import',
                        sku=data['subject'][:100] if data['subject'] else 'Importado SAP', # Use subject as SKU/Ref
                        descripcion=final_desc,
                        prioridad='media',
                        estado=incident_status,
                        fecha_reporte=created_at,
                        fecha_deteccion=created_at.date(),
                        hora_deteccion=created_at.time()
                    )
                    
                    # Override created_at which is auto_now_add
                    incident.created_at = created_at
                    
                    if not dry_run:
                        incident.save()
                        # Force update created_at after save because auto_now_add overrides it on creation
                        Incident.objects.filter(pk=incident.pk).update(created_at=created_at)
                        total_created += 1
                    else:
                        self.stdout.write(f"Dry Run: Would create Incident SAP-{sap_id}")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row {sap_id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Finished. Scanned: {total_processed}. Created: {total_created}. Skipped: {total_skipped}."))
