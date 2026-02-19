# Generated manually

from django.db import migrations, models
from django.utils import timezone


def populate_data_reclamacao(apps, schema_editor):
    """Preenche data_reclamacao com created_at para registros com NULL"""
    Complaint = apps.get_model('core', 'Complaint')
    for complaint in Complaint.objects.filter(data_reclamacao__isnull=True):
        complaint.data_reclamacao = complaint.created_at.date() if complaint.created_at else timezone.now().date()
        complaint.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_complaint_tags_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_data_reclamacao, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='complaint',
            name='data_reclamacao',
            field=models.DateField(),
        ),
    ]

