from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Set up Stripe development configuration'

    def handle(self, *args, **options):
        self.stdout.write('Setting up Stripe development configuration...')
        
        # Check current settings
        self.stdout.write(f'Current Stripe Secret Key: {settings.STRIPE_SECRET_KEY[:20]}...')
        self.stdout.write(f'Current Stripe Publishable Key: {settings.STRIPE_PUBLISHABLE_KEY[:20]}...')
        
        if settings.STRIPE_SECRET_KEY == 'sk_test_your_stripe_key':
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  Stripe is not configured! You have two options:\n\n'
                    'Option 1: Set up real Stripe keys\n'
                    '1. Go to https://dashboard.stripe.com/\n'
                    '2. Sign up or log in\n'
                    '3. Go to Developers → API keys\n'
                    '4. Copy your publishable key and secret key\n'
                    '5. Create a .env file in your project root with:\n'
                    '   STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key\n'
                    '   STRIPE_SECRET_KEY=sk_test_your_actual_key\n\n'
                    'Option 2: Use development mode\n'
                    'The application will automatically skip payment processing\n'
                    'when using the default placeholder keys.\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Stripe is configured!')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Setup complete!')
        ) 