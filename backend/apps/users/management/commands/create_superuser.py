"""
Management command to create a superuser, with non-interactive options.
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser with the specified details, prompting for a password if not provided.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Specifies the username for the superuser.')
        parser.add_argument('--email', type=str, help='Specifies the email for the superuser.')
        parser.add_argument('--password', type=str, help='Specifies the password for the superuser.')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']

        if not username:
            raise CommandError("Username is required. Use --username.")
        if not email:
            raise CommandError("Email is required. Use --email.")

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists.'))
            return

        if not password:
            # If password is not provided, Django's create_superuser will prompt for it securely
            self.stdout.write(self.style.SUCCESS(f'Creating superuser "{username}". Please enter a password.'))
            try:
                User.objects.create_superuser(username=username, email=email)
            except Exception as e:
                raise CommandError(f'Error creating superuser: {e}')
        else:
            # Non-interactive creation
            try:
                User.objects.create_superuser(username=username, email=email, password=password)
            except Exception as e:
                raise CommandError(f'Error creating superuser: {e}')

        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
