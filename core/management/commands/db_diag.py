from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Diagnostic: List all tables and their row counts"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # CockroachDB/Postgres query to get all tables in public schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write(self.style.SUCCESS(f"Found {len(tables)} tables in DB:"))
            
            for table in sorted(tables):
                try:
                    cursor.execute(f'SELECT count(*) FROM "{table}"')
                    count = cursor.fetchone()[0]
                    self.stdout.write(f"  - {table}: {count} rows")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  - {table}: Error counting: {e}"))
