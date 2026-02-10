import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import User

def check_user(username):
    print("=" * 50)
    print(f"Checking user: {username}")
    print("=" * 50)
    u = User.objects.filter(username=username).first()
    if u:
        print(f"ID: {u.id}")
        print(f"Username: {u.username}")
        print(f"Full Name: {u.full_name}")
        print(f"Email: {u.email}")
        print(f"Active: {u.is_active}")
        print(f"Role: {u.role}")
        print(f"Has Usable Password: {u.has_usable_password()}")
        # Check if password looks like a hash
        is_hashed = u.password.startswith('pbkdf2_sha256$') or u.password.startswith('argon2$') or u.password.startswith('bcrypt$')
        print(f"Is Password Hashed: {is_hashed}")
        if not is_hashed:
            print("WARNING: Password is NOT hashed (appears to be plain text)")
        
        # TEST PASSWORD
        test_pwd = 'anto1234'
        is_correct = u.check_password(test_pwd)
        print(f"Test Password '{test_pwd}' is CORRECT: {is_correct}")
    else:
        print("User NOT found")
    print("=" * 50)

if __name__ == "__main__":
    check_user('rcruz')
    # Also check a few other users to see general state
    print("\nGeneral User State:")
    for user in User.objects.all()[:10]:
        print(f" - {user.username} ({user.role}): Active={user.is_active}")
