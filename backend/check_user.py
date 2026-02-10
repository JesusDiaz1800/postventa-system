#!/usr/bin/env python
"""Script to check if user 66 exists in database"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import User

print("=" * 50)
print("Database User Check")
print("=" * 50)
print(f"Total users: {User.objects.count()}")
print(f"User 66 exists: {User.objects.filter(id=66).exists()}")
print("\nAll users:")
for user in User.objects.all().order_by('id'):
    print(f"  ID: {user.id}, Username: {user.username}, Active: {user.is_active}, Role: {user.role}")
print("=" * 50)
