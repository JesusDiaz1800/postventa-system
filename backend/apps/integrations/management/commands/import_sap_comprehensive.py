import logging
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.utils.timezone import make_aware
from apps.incidents.models import Incident, User
from apps.documents.models import VisitReport, DocumentStatus
from django.utils import timezone
import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import COMPREHENSIVE historical service calls from SAP as Incidents + Visit Reports'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Limit records to import')
        parser.add_argument('--dry-run', action='store_true', help='Run without saving')
        parser.add_argument('--generate-pdfs', action='store_true', help='Generate PDFs for created reports (Slow)')

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        gen_pdfs = options['generate_pdfs']
        
        self.stdout.write(self.style.WARNING("Starting ROBUST SAP Historical Import..."))
        
        if 'sap_db' not in connections:
            self.stdout.write(self.style.ERROR("Error: 'sap_db' connection not defined"))
            return

        # 1. System User
        system_user, _ = User.objects.get_or_create(
            email='sap_import@system.local',
            defaults={'first_name': 'SAP', 'last_name': 'History', 'username': 'sap_import', 'is_active': False}
        )
        if hasattr(system_user, 'set_unusable_password'):
            system_user.set_unusable_password()
            system_user.save()

        # 2. SIMPLIFIED FILTER (Conservative Approach)
        # Based on analysis: Keywords match ~1,900 TEMPLATE records (false positives)
        # STRICT FILTER: Only Post-Venta codes that are verifiably incidents
        
        target_problem_types = [33, 16]  # 33=Post-Venta, 16=Ver Filtracion (53 records)
        # callType 1 = Post-Vent (26 records verified)
        
        pt_filter = ",".join(map(str, target_problem_types))

        # UDF Fields
        udf_fields = ['U_NX_OBS_MATRIZ', 'U_NX_OBS_MURO', 'U_NX_OBS_LOSA', 'U_NX_OBS_ALMAC', 'U_NX_OBS_EXTER', 'descrption', 'U_NX_OBS_PRE_ARM']
        udf_select = ", ".join(udf_fields)

        query = f"""
        SELECT callID, customer, custmrName, subject, createDate, status, problemTyp, callType,
               {udf_select}
        FROM OSCL 
        WHERE 
           callType = 1
           OR problemTyp IN ({pt_filter})
        ORDER BY createDate DESC
        """

        conn = connections['sap_db']
        cursor = conn.cursor()
        cursor.execute(query)
        
        columns = [col[0] for col in cursor.description]
        
        total_created = 0
        total_skipped = 0
        
        # Fetch logic similar to previous...
        rows = cursor.fetchall() # Retrieve all to filter in python or iterate
        
        self.stdout.write(f"Found {len(rows)} potential candidates.")
        
        for idx, row in enumerate(rows):
            if limit and total_created >= limit:
                break
                
            data = dict(zip(columns, row))
            sap_id = data['callID']
            
            # --- INCIDENCIA ---
            if Incident.objects.filter(sap_call_id=sap_id).exists():
                total_skipped += 1
                continue # or update? for now skip

            # Mapper Status
            status_map = {-3: 'cerrado', -1: 'abierto'}
            status_val = status_map.get(data['status'], 'abierto')
            
            # Dates
            created_at = data['createDate']
            if isinstance(created_at, datetime.datetime):
                    if timezone.is_naive(created_at): created_at = make_aware(created_at)
            else: created_at = timezone.now()

            # Description for Incident (Summary)
            # We want the incident description to be concise if we have a full report
            # But let's keep the full concatenation for searchability
            desc_parts = [f"Ref SAP: {data['subject']}"]
            if data['descrption']: desc_parts.append(data['descrption'])
            final_incident_desc = "\n".join(desc_parts)

            incident = Incident(
                code=f"SAP-{sap_id}",
                sap_call_id=sap_id,
                created_by=system_user,
                cliente=data['custmrName'] or 'Sin Nombre',
                customer_code=data['customer'] or 'N/A',
                provider='SAP Import',
                sku=data['subject'][:100] if data['subject'] else 'Importado',
                descripcion=final_incident_desc,
                prioridad='media',
                estado=status_val,
                fecha_reporte=created_at
            )

            # --- REPORTE DE VISITA ---
            # Create VisitReport linked to this incident
            # Map UDFs to specific sections
            
            # Generate Report Number manually to avoid collisions or let save() handle?
            # save() handles it based on incident code.
            
            visit_report = VisitReport(
                related_incident=None, # Set after saving incident
                visit_date=created_at,
                client_name=data['custmrName'] or 'Sin Nombre',
                client_rut=data['customer'] or '',
                project_name="Importado SAP", # Unknown from limited fields
                address="Dirección SAP", 
                salesperson="Vendedor SAP",
                technician="Técnico SAP",
                visit_reason=f"Importación Histórica (Tipo {data['problemTyp']})",
                
                # MAPPING UDFs!
                matrix_observations=data['U_NX_OBS_MATRIZ'] or '',
                wall_observations=data['U_NX_OBS_MURO'] or '',
                slab_observations=data['U_NX_OBS_LOSA'] or '',
                storage_observations=data['U_NX_OBS_ALMAC'] or '',
                pre_assembled_observations=data['U_NX_OBS_PRE_ARM'] or '',
                exterior_observations=data['U_NX_OBS_EXTER'] or '',
                general_observations=data['descrption'] or '',
                
                status=DocumentStatus.CLOSED if status_val == 'cerrado' else DocumentStatus.APPROVED,
                sap_call_id=sap_id,
                sync_status='synced',
                created_by=system_user
            )

            if not dry_run:
                try:
                    with transaction.atomic():
                        incident.save()
                        # Update created_at
                        Incident.objects.filter(pk=incident.pk).update(created_at=created_at)
                        
                        visit_report.related_incident = incident
                        visit_report.save() # Generates number
                        
                        # Fix visit report timestamps
                        VisitReport.objects.filter(pk=visit_report.pk).update(created_at=created_at, visit_date=created_at)
                        
                        total_created += 1
                        
                        if gen_pdfs:
                            # CALL PDF GENERATION SERVICE HERE
                            # from apps.documents.services import generate_visit_report_pdf
                            # generate_visit_report_pdf(visit_report)
                            pass
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to import {sap_id}: {e}"))
            else:
                self.stdout.write(f"[Dry Run] Incident SAP-{sap_id} + VisitReport (with Obs Matriz: {bool(data['U_NX_OBS_MATRIZ'])})")
                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"Finished. Candidates: {len(rows)}. Actions: {total_created}."))
