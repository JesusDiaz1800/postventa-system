import os
import sys
import django

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.documents.models import DocumentAttachment
from apps.incidents.models import Incident

def verify_attachments():
    print("Verifying DocumentAttachments...")
    
    # Check for potential collisions
    # Find IDs that exist in both Incident and have VisitReport attachments
    
    attachments = DocumentAttachment.objects.values('document_id', 'document_type', 'id').order_by('document_id')
    
    print(f"Total Attachments: {len(attachments)}")
    
    # Group by ID
    by_id = {}
    for att in attachments:
        did = att['document_id']
        dtype = att['document_type']
        if did not in by_id:
            by_id[did] = set()
        by_id[did].add(dtype)
        
    print("\n--- IDs with mixed types ---")
    count_mixed = 0
    for did, types in by_id.items():
        if len(types) > 1:
            print(f"ID {did}: {types}")
            count_mixed += 1
            
    if count_mixed == 0:
        print("No mixed types found for same ID.")
    else:
        print(f"Found {count_mixed} IDs with mixed attachment types.")

    # Check specifically for ID 10 (example) or common IDs
    print("\n--- Sample Check (First 10) ---")
    for att in DocumentAttachment.objects.all()[:10]:
        print(f"ID: {att.id} | DocID: {att.document_id} | Type: {att.document_type} | Name: {att.filename}")

    # Check if any attachment has blank document_type
    print("\n--- Blank Status ---")
    blanks = DocumentAttachment.objects.filter(document_type='').count()
    print(f"Attachments with blank type: {blanks}")

if __name__ == '__main__':
    verify_attachments()
