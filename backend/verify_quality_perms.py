import os
import sys
import django
from unittest.mock import MagicMock

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.incidents.permissions import CanViewIncidents, CanManageIncidents, CanViewLabReports, CanCreateLabReports

def verify_permissions():
    print("=" * 50)
    print("Permission Verification for Role: quality")
    print("=" * 50)
    
    # Mock user and request
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.role = 'quality'
    
    mock_request = MagicMock()
    mock_request.user = mock_user
    
    # Permissions to test
    permissions = [
        CanViewIncidents(),
        CanManageIncidents(),
        CanViewLabReports(),
        CanCreateLabReports()
    ]
    
    all_passed = True
    for perm in permissions:
        result = perm.has_permission(mock_request, None)
        status = "PASSED" if result else "FAILED"
        print(f"{perm.__class__.__name__}: {status}")
        if not result:
            all_passed = False
            
    print("=" * 50)
    if all_passed:
        print("SUCCESS: All permissions are correctly assigned to 'quality' role.")
    else:
        print("FAILURE: Some permissions are missing for 'quality' role.")
    print("=" * 50)

if __name__ == "__main__":
    verify_permissions()
