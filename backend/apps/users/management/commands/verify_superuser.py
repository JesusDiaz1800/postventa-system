# backend/apps/users/management/commands/verify_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Verifies if at least one superuser exists in the database.'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.filter(is_superuser=True).first()
            self.stdout.write(self.style.SUCCESS(f'Verification successful. At least one superuser exists. Found: "{superuser.username}".'))
        else:
            self.stdout.write(self.style.ERROR('Verification failed. No superuser found in the database.'))
            self.stdout.write(self.style.WARNING('You can create one using: python manage.py create_superuser --username <name> --email <email>'))
