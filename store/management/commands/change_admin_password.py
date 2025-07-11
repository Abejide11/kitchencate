from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Change the admin dashboard password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            help='New admin password to set'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Run in interactive mode to enter password securely'
        )

    def handle(self, *args, **options):
        new_password = options['password']
        interactive = options['interactive']
        
        if interactive:
            import getpass
            new_password = getpass.getpass('Enter new admin password: ')
            confirm_password = getpass.getpass('Confirm new admin password: ')
            
            if new_password != confirm_password:
                self.stdout.write(
                    self.style.ERROR('Passwords do not match!')
                )
                return
        
        if not new_password:
            self.stdout.write(
                self.style.ERROR('Please provide a password using --password or --interactive')
            )
            return
        
        if len(new_password) < 6:
            self.stdout.write(
                self.style.WARNING('Password should be at least 6 characters long')
            )
            response = input('Continue anyway? (y/N): ')
            if response.lower() != 'y':
                return
        
        # Update the .env file
        env_file = Path(settings.BASE_DIR) / '.env'
        
        if env_file.exists():
            # Read existing .env file
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Check if ADMIN_DASHBOARD_PASSWORD already exists
            password_line_index = None
            for i, line in enumerate(lines):
                if line.startswith('ADMIN_DASHBOARD_PASSWORD='):
                    password_line_index = i
                    break
            
            if password_line_index is not None:
                # Update existing line
                lines[password_line_index] = f'ADMIN_DASHBOARD_PASSWORD={new_password}\n'
            else:
                # Add new line
                lines.append(f'ADMIN_DASHBOARD_PASSWORD={new_password}\n')
            
            # Write back to .env file
            with open(env_file, 'w') as f:
                f.writelines(lines)
        else:
            # Create new .env file
            with open(env_file, 'w') as f:
                f.write(f'ADMIN_DASHBOARD_PASSWORD={new_password}\n')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Admin password updated successfully!')
        )
        self.stdout.write(
            f'New password: {new_password}'
        )
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Important:\n'
                '1. Restart your Django server for changes to take effect\n'
                '2. Keep this password secure and don\'t share it\n'
                '3. Consider using environment variables in production'
            )
        ) 