from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Set up and verify payment configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-flutterwave',
            action='store_true',
            help='Check Flutterwave configuration',
        )
        parser.add_argument(
            '--test-flutterwave',
            action='store_true',
            help='Test Flutterwave connection',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Payment System Setup & Verification')
        )
        
        if options['check_flutterwave'] or options['test_flutterwave']:
            self.check_flutterwave_configuration()
            
        if options['test_flutterwave']:
            self.test_flutterwave_connection()
        
        self.display_payment_status()

    def check_flutterwave_configuration(self):
        """Check Flutterwave configuration"""
        self.stdout.write('\n📋 Flutterwave Configuration Check:')
        
        # Check API keys
        public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', None)
        secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', None)
        encryption_key = getattr(settings, 'FLUTTERWAVE_ENCRYPTION_KEY', None)
        webhook_secret = getattr(settings, 'FLUTTERWAVE_WEBHOOK_SECRET', None)
        
        if not public_key or public_key == 'FLWPUBK_TEST_your_flutterwave_public_key':
            self.stdout.write(
                self.style.WARNING('❌ FLUTTERWAVE_PUBLIC_KEY not configured')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ FLUTTERWAVE_PUBLIC_KEY: {public_key[:20]}...')
            )
        
        if not secret_key or secret_key == 'FLWSECK_TEST_your_flutterwave_secret_key':
            self.stdout.write(
                self.style.WARNING('❌ FLUTTERWAVE_SECRET_KEY not configured')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ FLUTTERWAVE_SECRET_KEY: {secret_key[:20]}...')
            )
        
        if not encryption_key or encryption_key == 'your_flutterwave_encryption_key':
            self.stdout.write(
                self.style.WARNING('❌ FLUTTERWAVE_ENCRYPTION_KEY not configured')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ FLUTTERWAVE_ENCRYPTION_KEY: {encryption_key[:20]}...')
            )
        
        if not webhook_secret or webhook_secret == 'your_flutterwave_webhook_secret':
            self.stdout.write(
                self.style.WARNING('❌ FLUTTERWAVE_WEBHOOK_SECRET not configured')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ FLUTTERWAVE_WEBHOOK_SECRET: {webhook_secret[:20]}...')
            )

    def test_flutterwave_connection(self):
        """Test Flutterwave API connection"""
        self.stdout.write('\n🔌 Testing Flutterwave Connection:')
        
        try:
            import requests
            
            # Test API connection by making a simple request
            headers = {
                "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.flutterwave.com/v3/transactions",
                headers=headers,
                params={"limit": 1}
            )
            
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS('✅ Flutterwave connection successful')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Flutterwave connection failed: HTTP {response.status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Flutterwave connection error: {e}')
            )

    def display_payment_status(self):
        """Display payment methods status"""
        self.stdout.write('\n💳 Payment Methods Status:')
        
        payment_methods = [
            {
                'name': 'Flutterwave Card',
                'status': '✅ Ready' if self.is_flutterwave_configured() else '❌ Needs Flutterwave Setup',
                'description': 'Visa, Mastercard, Verve via Flutterwave'
            },
            {
                'name': 'Flutterwave Bank Transfer',
                'status': '✅ Ready' if self.is_flutterwave_configured() else '❌ Needs Flutterwave Setup',
                'description': 'Direct bank transfer via Flutterwave'
            },
            {
                'name': 'Flutterwave USSD',
                'status': '✅ Ready' if self.is_flutterwave_configured() else '❌ Needs Flutterwave Setup',
                'description': 'USSD payment codes via Flutterwave'
            },
            {
                'name': 'Flutterwave Mobile Money',
                'status': '✅ Ready' if self.is_flutterwave_configured() else '❌ Needs Flutterwave Setup',
                'description': 'Mobile money wallets via Flutterwave'
            },
            {
                'name': 'Flutterwave QR Code',
                'status': '✅ Ready' if self.is_flutterwave_configured() else '❌ Needs Flutterwave Setup',
                'description': 'QR code payments via Flutterwave'
            },
            {
                'name': 'Manual Bank Transfer',
                'status': '✅ Ready',
                'description': 'Manual verification required'
            },
            {
                'name': 'USSD Payment (Demo)',
                'status': '⚠️ Demo Mode',
                'description': 'Placeholder - needs real USSD integration'
            },
            {
                'name': 'Mobile Money (Demo)',
                'status': '⚠️ Demo Mode',
                'description': 'Placeholder - needs real mobile money integration'
            }
        ]
        
        for method in payment_methods:
            self.stdout.write(f'   {method["name"]:<30} {method["status"]}')
            self.stdout.write(f'   {"":<30} {method["description"]}')
            self.stdout.write('')

    def is_flutterwave_configured(self):
        """Check if Flutterwave is properly configured"""
        public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', None)
        secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', None)
        
        return (public_key and public_key != 'FLWPUBK_TEST_your_flutterwave_public_key' and
                secret_key and secret_key != 'FLWSECK_TEST_your_flutterwave_secret_key') 