from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Create admin user for deployment'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists!')
            )
            return
        
        # Create admin user
        try:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@kitchencrate.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user created successfully!')
            )
            self.stdout.write(f'Username: {admin_user.username}')
            self.stdout.write(f'Email: {admin_user.email}')
            self.stdout.write(f'Password: admin123')
            self.stdout.write(f'Is Staff: {admin_user.is_staff}')
            self.stdout.write(f'Is Superuser: {admin_user.is_superuser}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {str(e)}')
            )
        
        # Display admin dashboard password
        admin_password = getattr(settings, 'ADMIN_DASHBOARD_PASSWORD', 'admin123')
        self.stdout.write(
            self.style.SUCCESS(f'\n🔐 Admin Dashboard Password: {admin_password}')
        ) 