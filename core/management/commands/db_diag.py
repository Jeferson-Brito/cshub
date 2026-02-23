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

            # Check for permission duplicates (IntegrityError investigation)
            self.stdout.write(self.style.SUCCESS("\nPermission/ContentType Audit:"))
            try:
                cursor.execute("""
                    SELECT ct.app_label, ct.model, p.codename, COUNT(*) 
                    FROM auth_permission p 
                    JOIN django_content_type ct ON p.content_type_id = ct.id 
                    GROUP BY ct.app_label, ct.model, p.codename 
                    HAVING COUNT(*) > 1
                """)
                dupes = cursor.fetchall()
                if dupes:
                    for d in dupes:
                        self.stdout.write(self.style.ERROR(f"  - Duplicate: {d[0]}.{d[1]} - {d[2]} ({d[3]} times)"))
                else:
                    self.stdout.write("  - No duplicate permissions found in auth_permission.")
                
                # Check specific content type causing error
                cursor.execute("SELECT id, app_label, model FROM django_content_type WHERE model = 'weeklyverificationkpi'")
                ct_info = cursor.fetchone()
                if ct_info:
                    self.stdout.write(f"  - ContentType for weeklyverificationkpi: id={ct_info[0]}, app={ct_info[1]}")
                else:
                    self.stdout.write("  - ContentType for weeklyverificationkpi NOT FOUND.")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error auditing permissions: {e}"))
