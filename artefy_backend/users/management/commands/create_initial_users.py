# users/management/commands/create_initial_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates initial users for Artefy application'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Create superadmin
        superadmin = User.objects.create_user(
            username='superadmin',
            email='superadmin@artefy.com',
            password='Admin123!',
            role='superadmin'
        )
        superadmin.is_superuser = True
        superadmin.is_staff = True
        superadmin.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully created superadmin with hash: {superadmin.password}'))

        # Create moderator
        moderator = User.objects.create_user(
            username='moderator',
            email='moderator@artefy.com',
            password='Mod123!',
            role='moderator'
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created moderator with hash: {moderator.password}'))

        # Create regular users
        user1 = User.objects.create_user(
            username='user1',
            email='user1@artefy.com',
            password='User123!',
            role='user'
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created user1 with hash: {user1.password}'))

        user2 = User.objects.create_user(
            username='user2',
            email='user2@artefy.com',
            password='User123!',
            role='user'
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created user2 with hash: {user2.password}'))