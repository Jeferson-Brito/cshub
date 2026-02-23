from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection

class Command(BaseCommand):
    help = "Fix duplicate permissions that cause IntegrityError during migrate"

    def handle(self, *args, **options):
        self.stdout.write("Checking for duplicate permissions...")
        
        with connection.cursor() as cursor:
            # Find duplicates
            cursor.execute("""
                SELECT content_type_id, codename, COUNT(*)
                FROM auth_permission
                GROUP BY content_type_id, codename
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            
            if not duplicates:
                self.stdout.write(self.style.SUCCESS("No duplicate permissions found."))
                return

            for ct_id, codename, count in duplicates:
                self.stdout.write(self.style.WARNING(f"Fixing {count} duplicates for {codename} (CT: {ct_id})"))
                
                # Get all IDs for this specific permission
                cursor.execute("""
                    SELECT id FROM auth_permission 
                    WHERE content_type_id = %s AND codename = %s
                    ORDER BY id ASC
                """, [ct_id, codename])
                ids = [row[0] for row in cursor.fetchall()]
                
                # Keep the first ID, delete others
                ids_to_delete = ids[1:]
                if ids_to_delete:
                    self.stdout.write(f"  Deleting IDs: {ids_to_delete}")
                    cursor.execute("DELETE FROM auth_permission WHERE id = ANY(%s)", [ids_to_delete])

        self.stdout.write(self.style.SUCCESS("Permissions cleanup complete."))
