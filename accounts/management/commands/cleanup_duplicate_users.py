from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Count

class Command(BaseCommand):
    help = 'Clean up duplicate users with the same email address'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find users with duplicate emails
        duplicate_emails = User.objects.values('email').annotate(
            count=Count('email')
        ).filter(count__gt=1, email__isnull=False).exclude(email='')
        
        if not duplicate_emails:
            self.stdout.write(
                self.style.SUCCESS('No duplicate email addresses found!')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {len(duplicate_emails)} email addresses with duplicates:')
        )
        
        total_deleted = 0
        
        for email_data in duplicate_emails:
            email = email_data['email']
            count = email_data['count']
            
            self.stdout.write(f'\nEmail: {email} (found {count} times)')
            
            # Get all users with this email, ordered by date joined (oldest first)
            users = list(User.objects.filter(email=email).order_by('date_joined'))
            
            # Keep the first (oldest) user, delete the rest
            users_to_delete = users[1:]
            
            for user in users:
                status = "KEEP" if user == users[0] else "DELETE"
                self.stdout.write(f'  - {user.username} (joined: {user.date_joined}) - {status}')
            
            if not dry_run:
                # Delete duplicate users
                deleted_count = len(users_to_delete)
                for user in users_to_delete:
                    user.delete()
                total_deleted += deleted_count
                self.stdout.write(
                    self.style.SUCCESS(f'  Deleted {deleted_count} duplicate user(s)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Would delete {len(users_to_delete)} user(s) (dry run)')
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDry run complete. Would delete {total_deleted} duplicate users.')
            )
            self.stdout.write(
                self.style.WARNING('Run without --dry-run to actually delete the duplicates.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nCleanup complete! Deleted {total_deleted} duplicate users.')
            ) 