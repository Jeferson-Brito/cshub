from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adiciona índices compostos ao modelo Complaint para acelerar os padrões
    de query mais comuns: filtro por (department + status), (department + created_at)
    e (department + analista).
    """

    dependencies = [
        ("core", "0057_reset_all_passwords"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="complaint",
            index=models.Index(
                fields=["department", "status"],
                name="complaint_dept_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="complaint",
            index=models.Index(
                fields=["department", "created_at"],
                name="complaint_dept_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="complaint",
            index=models.Index(
                fields=["department", "analista"],
                name="complaint_dept_analista_idx",
            ),
        ),
    ]
