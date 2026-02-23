from django.db import migrations


def reset_all_passwords(apps, schema_editor):
    """
    Emergency recovery: reset password for primary admin user.
    All users lost login access after a Render redeploy.
    Sets password for jeffersonbrito2455@gmail.com to Nexus@2025.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # First, try to recover the main admin account
    reset_count = 0
    errors = []

    # Target: the main admin user by email
    targets = [
        'jeffersonbrito2455@gmail.com',
    ]

    for email in targets:
        try:
            user = User.objects.get(email=email)
            user.set_password('Nexus@2025')
            user.is_active = True
            user.ativo = True
            user.save(update_fields=['password', 'is_active', 'ativo'])
            print(f'[0056] ✅ Password reset for {user.email} (id={user.id})')
            reset_count += 1
        except User.DoesNotExist:
            print(f'[0056] ⚠️  User {email} not found.')
        except Exception as e:
            errors.append(str(e))
            print(f'[0056] ❌ Error resetting {email}: {e}')

    # Also reset all admin/gestor users so access can be restored
    try:
        admins = User.objects.filter(role__in=['administrador', 'gestor'], is_active=True)
        for user in admins:
            if user.email not in targets:  # Don't double-reset the ones above
                user.set_password('Nexus@2025')
                user.ativo = True
                user.save(update_fields=['password', 'ativo'])
                print(f'[0056] ✅ Admin/Gestor password reset: {user.email} (id={user.id})')
                reset_count += 1
    except Exception as e:
        print(f'[0056] ❌ Error resetting admin/gestor users: {e}')

    print(f'[0056] Done. Total passwords reset: {reset_count}')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_add_auditoria_feedback_fields'),
    ]

    operations = [
        migrations.RunPython(reset_all_passwords, migrations.RunPython.noop),
    ]
