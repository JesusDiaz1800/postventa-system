import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import User

def reset_password(username, new_password):
    print(f"Attempting to reset password for {username}...")
    u = User.objects.filter(username=username).first()
    if u:
        u.set_password(new_password)
        u.save()
        # Verify immediately
        if u.check_password(new_password):
            print(f"SUCCESS: Password for {username} has been reset and verified.")
        else:
            print(f"FAILURE: Password reset for {username} could not be verified.")
    else:
        print(f"ERROR: User {username} not found.")

if __name__ == "__main__":
    reset_password('rcruz', 'anto1234')
