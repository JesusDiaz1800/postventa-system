import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.documents.models import DocumentAttachment, VisitReport

print("--- INSPECTING DOCUMENT ATTACHMENTS ---")
count = DocumentAttachment.objects.count()
print(f"Total Attachments: {count}")

print("\nLast 10 Attachments:")
last_atts = DocumentAttachment.objects.order_by('-uploaded_at')[:10]
for att in last_atts:
    print(f"ID: {att.id}, DocType: {att.document_type}, DocID: {att.document_id}, File: {att.file}, Exists: {os.path.exists(att.file.path) if att.file else 'NoFile'}")

print("\n--- CHECKING VISIT REPORTS ---")
last_report = VisitReport.objects.last()
if last_report:
    print(f"Last Report ID: {last_report.id}, Order: {last_report.order_number}")
    
    # Check linked attachments
    linked_atts = DocumentAttachment.objects.filter(document_id=last_report.id, document_type='visit_report')
    print(f"Attachments for Last Report ({linked_atts.count()}):")
    for att in linked_atts:
        print(f" - {att.file.path} (Exists: {os.path.exists(att.file.path) if att.file else 'NoFile'})")
else:
    print("No Visit Reports found.")
