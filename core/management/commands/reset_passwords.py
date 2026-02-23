"""
Emergency password reset command.
Resets ALL user passwords to 'Nexus@2025'.
Safe to run multiple times - idempotent.
Remove from startCommand once access is recovered.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = "Emergency: reset all user passwords to Nexus@2025"

    def handle(self, *args, **options):
        User = get_user_model()

        new_hash = make_password('Nexus@2025')

        # Direct SQL-level update to bypass any model issues
        count = User.objects.all().update(
            password=new_hash,
        )

        self.stdout.write(self.style.SUCCESS(
            f'✅ Emergency password reset: {count} users updated to Nexus@2025'
        ))

        # Also ensure all users are active
        User.objects.all().update(is_active=True, ativo=True)
        self.stdout.write(self.style.SUCCESS('✅ All users set to active'))

        # Log first 5 users for debugging
        for u in User.objects.all()[:5]:
            self.stdout.write(f'  - {u.email} (username={u.username}, active={u.is_active}, ativo={u.ativo})')
