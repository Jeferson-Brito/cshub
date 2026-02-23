from django.db import migrations


def create_departments_and_fix_admin(apps, schema_editor):
    Department = apps.get_model('core', 'Department')
    User = apps.get_model('core', 'User')

    # Cria departamentos padrão do sistema
    cs_clientes, _ = Department.objects.get_or_create(
        slug='cs-clientes',
        defaults={'name': 'CS Clientes', 'description': 'Central de Relacionamento com Clientes'},
    )
    Department.objects.get_or_create(
        slug='nrs-suporte',
        defaults={'name': 'NRS Suporte', 'description': 'NRS Suporte Técnico'},
    )

    # Vincula o admin ao CS Clientes (departamento principal do sistema)
    User.objects.filter(username='admin').update(department_id=cs_clientes.id)


def reverse_departments(apps, schema_editor):
    Department = apps.get_model('core', 'Department')
    Department.objects.filter(slug__in=['cs-clientes', 'nrs-suporte']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_create_admin_user'),
    ]

    operations = [
        migrations.RunPython(create_departments_and_fix_admin, reverse_code=reverse_departments),
    ]
