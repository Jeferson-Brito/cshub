"""
Management command to migrate all data from Supabase (source) to CockroachDB (default).

Usage:
    Set SOURCE_DATABASE_URL env var to the Supabase connection string, then run:
        python manage.py migrate_to_cockroach

The command copies data table by table, respecting FK order.
"""

import os
import psycopg2
import psycopg2.extras
from django.core.management.base import BaseCommand
from django.db import connection


# Tables in dependency order (parents before children to respect FKs)
TABLES_IN_ORDER = [
    # Django internals
    "django_content_type",
    "auth_permission",
    "auth_group",
    "auth_group_permissions",
    # Core: basic data
    "core_department",
    "core_turno",
    "core_store",
    # Core: users (depends on department)
    "core_user",
    "core_user_groups",
    "core_user_user_permissions",
    # Core: operational data
    "core_auditlog",
    "core_activity",
    "core_complaint",
    "core_evento",
    "core_ferramentaia",
    "core_artigobaseconhecimento",
    "core_observacaodesempenho",
    "core_indicadordesempenho",
    "core_metamensalglobal",
    "core_folgamanual",
    # Escala
    "core_analistaescala",
    "core_escala",
    # Kanban board
    "core_kanbanboard",
    "core_boardmembership",
    "core_kanbanlist",
    "core_cardlabel",
    "core_kanbancard",
    "core_kanbancard_assigned_to",
    "core_kanbancard_labels",
    "core_cardcomment",
    "core_cardattachment",
    "core_cardactivity",
    # Cartao (old board)
    "core_lista",
    "core_cartao",
    "core_cartao_membros",
    "core_cartaoanexo",
    "core_cartaocomentario",
    "core_quadroetiqueta",
    "core_cartao_etiquetas",
    # Checklist
    "core_checklist",
    "core_checklistitem",
    # Routine / Task
    "core_routine",
    "core_task",
    "core_routinelog",
    # Refund
    "core_refundrequest",
    "core_refundrequestattachment",
    # Store audit
    "core_storeaudit",
    "core_storeaudititem",
    "core_storeauditissue",
    "core_storeauditlog" if False else None,    # skip if doesn't exist
    "core_storeviewersession",
    "core_configuracaoauditoria",
    "core_auditoriaatendimento",
    # KPI / quota
    "core_weeklyverificationkpi",
    "core_dailyauditquota",
    "core_analystassignment",
    # Notifications
    "core_systemnotification",
]


class Command(BaseCommand):
    help = "Migrates all data from Supabase (SOURCE_DATABASE_URL) to CockroachDB (default DB)"

    def handle(self, *args, **options):
        source_url = os.environ.get("SOURCE_DATABASE_URL")
        if not source_url:
            self.stderr.write(self.style.ERROR(
                "SOURCE_DATABASE_URL environment variable is not set."
            ))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Connecting to Supabase source..."))
        try:
            src_conn = psycopg2.connect(source_url, sslmode="require")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to connect to source DB: {e}"))
            return

        src_conn.autocommit = True
        src_cur = src_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        tables = [t for t in TABLES_IN_ORDER if t]  # filter None

        total_copied = 0

        with connection.cursor() as dest_cur:
            for table in tables:
                # Check if table exists in source
                src_cur.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = %s)",
                    [table]
                )
                if not src_cur.fetchone()[0]:
                    self.stdout.write(f"  ⚠️  Skipping {table} (not in source)")
                    continue

                # Check if table exists in dest
                try:
                    dest_cur.execute(f'SELECT 1 FROM "{table}" LIMIT 1')
                except Exception:
                    self.stdout.write(f"  ⚠️  Skipping {table} (not in destination)")
                    connection.rollback()
                    continue

                # Count source rows
                src_cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = src_cur.fetchone()[0]

                if count == 0:
                    self.stdout.write(f"  — {table}: empty, skipping")
                    continue

                self.stdout.write(f"  → Copying {table} ({count} rows)...")

                # Fetch all rows from source
                src_cur.execute(f'SELECT * FROM "{table}"')
                rows = src_cur.fetchall()

                if not rows:
                    continue

                # Get column names
                columns = [desc[0] for desc in src_cur.description]
                col_list = ", ".join(f'"{c}"' for c in columns)
                placeholders = ", ".join(["%s"] * len(columns))

                # Clear destination table before inserting
                try:
                    dest_cur.execute(f'DELETE FROM "{table}"')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f"    Could not clear {table}: {e}"
                    ))
                    connection.rollback()
                    continue

                # Batch insert
                insert_sql = f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
                try:
                    for row in rows:
                        dest_cur.execute(insert_sql, list(row))
                    connection.commit()
                    self.stdout.write(self.style.SUCCESS(f"    ✓ {count} rows copied"))
                    total_copied += count
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    ✗ Error copying {table}: {e}"))
                    connection.rollback()

        src_cur.close()
        src_conn.close()

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Migration complete! {total_copied} total rows copied to CockroachDB."
        ))
        self.stdout.write(
            "Next: create a superuser if not migrated, then remove SOURCE_DATABASE_URL from Render."
        )
