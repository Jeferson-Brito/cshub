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
    help = "Emergency: reset all user passwords to Nexus@2025 and ensure admin exists"

    def handle(self, *args, **options):
        User = get_user_model()
        new_hash = make_password('Nexus@2025')

        # 1. Diagnostic: List all users
        all_users = User.objects.all()
        self.stdout.write(self.style.WARNING(f'Total users in DB: {all_users.count()}'))
        for u in all_users:
            self.stdout.write(f'  - Found user: {u.email} (username={u.username}, role={u.role}, active={u.is_active}/{u.ativo})')

        # 2. Ensure specific admin exists
        admin_email = 'jeffersonbrito2455@gmail.com'
        if not User.objects.filter(email__iexact=admin_email).exists():
            self.stdout.write(self.style.WARNING(f'User {admin_email} NOT FOUND. Creating...'))
            User.objects.create(
                username='jefferson',
                email=admin_email,
                password=new_hash,
                role='administrador',
                is_staff=True,
                is_superuser=True,
                is_active=True,
                ativo=True
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Created user {admin_email}'))

        # 3. Reset all passwords
        count = User.objects.all().update(
            password=new_hash,
            is_active=True,
            ativo=True
        )

        self.stdout.write(self.style.SUCCESS(
            f'✅ Emergency password reset: {count} users updated to Nexus@2025'
        ))

