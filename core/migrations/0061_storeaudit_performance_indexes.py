from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adiciona índices de performance para acelerar o dashboard de verificação de lojas.
    """

    dependencies = [
        ("core", "0060_auditoriaatendimento_link_conversa"),
    ]

    operations = [
        # Índices para StoreAudit
        migrations.AddIndex(
            model_name="storeaudit",
            index=models.Index(
                fields=["analyst", "created_at"],
                name="core_storaud_analyst_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="storeaudit",
            index=models.Index(
                fields=["store", "created_at"],
                name="core_storaud_store_idx",
            ),
        ),
        
        # Índices para StoreAuditIssue
        migrations.AddIndex(
            model_name="storeauditissue",
            index=models.Index(
                fields=["status", "store"],
                name="core_storaudiss_status_idx",
            ),
        ),
        
        # Índices para AnalystAssignment
        migrations.AddIndex(
            model_name="analystassignment",
            index=models.Index(
                fields=["analyst", "active"],
                name="core_analystass_active_idx",
            ),
        ),
    ]
