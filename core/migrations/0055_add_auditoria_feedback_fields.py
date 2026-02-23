from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_create_departments'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditoriaatendimento',
            name='feedback_data',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='Data da Conversa',
                help_text='Data em que o gestor conversou com o analista sobre o alerta'
            ),
        ),
        migrations.AddField(
            model_name='auditoriaatendimento',
            name='feedback_gestor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='feedbacks_dados',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Gestor que conversou'
            ),
        ),
    ]
