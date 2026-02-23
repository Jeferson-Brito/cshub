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

        self.stdout.write(self.style.NOTICE("Starting emergency password reset diagnostic..."))

        # 1. Diagnostic: List all users
        all_users = User.objects.all()
        user_count = all_users.count()
        self.stdout.write(self.style.WARNING(f'Total users in DB: {user_count}'))
        
        for u in all_users:
            self.stdout.write(f'  [USER] id={u.id}, email="{u.email}", username="{u.username}", role="{u.role}", active={u.is_active}/{u.ativo}')

        # 2. Ensure specific admin exists
        admin_email = 'jeffersonbrito2455@gmail.com'
        # Search using lowercase to be absolutely sure
        admin_user = User.objects.filter(email__iexact=admin_email).first()
        
        if not admin_user:
            self.stdout.write(self.style.WARNING(f'User {admin_email} NOT FOUND. Creating a new one...'))
            try:
                # Try to see if username 'jefferson' exists first to avoid conflict
                username = 'jefferson'
                suffix = 1
                while User.objects.filter(username=username).exists():
                    username = f'jefferson{suffix}'
                    suffix += 1
                
                admin_user = User.objects.create(
                    username=username,
                    email=admin_email,
                    password=new_hash,
                    role='administrador',
                    is_staff=True,
                    is_superuser=True,
                    is_active=True,
                    ativo=True
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Created fresh admin user: {admin_user.email} (username={admin_user.username})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to create admin user: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing admin user {admin_user.email}. Updating...'))
            admin_user.is_active = True
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.ativo = True
            admin_user.password = new_hash
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Updated existing admin user: {admin_user.email}'))

        # 3. Reset all other passwords
        count = User.objects.all().update(
            password=new_hash,
            is_active=True,
            ativo=True
        )

        self.stdout.write(self.style.SUCCESS(
            f'✅ Emergency password reset: {count} total users updated/ensured to Nexus@2025'
        ))

