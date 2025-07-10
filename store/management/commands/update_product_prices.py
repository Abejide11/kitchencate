from django.core.management.base import BaseCommand
from store.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Multiply all product prices by 1500 to convert to Nigerian Naira'

    def add_arguments(self, parser):
        parser.add_argument(
            '--multiplier',
            type=float,
            default=1500,
            help='Multiplier for product prices (default: 1500)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually updating the database'
        )

    def handle(self, *args, **options):
        multiplier = Decimal(str(options['multiplier']))
        dry_run = options['dry_run']
        
        products = Product.objects.all()
        
        if not products.exists():
            self.stdout.write(
                self.style.WARNING('No products found in the database.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {products.count()} products to update.')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made to the database.')
            )
        
        updated_count = 0
        
        for product in products:
            old_price = product.price
            new_price = old_price * multiplier
            
            if dry_run:
                self.stdout.write(
                    f'Would update: {product.name} - ₦{old_price} → ₦{new_price}'
                )
            else:
                product.price = new_price
                product.save()
                self.stdout.write(
                    f'Updated: {product.name} - ₦{old_price} → ₦{new_price}'
                )
            
            updated_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN: Would update {updated_count} products with multiplier {multiplier}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} products with multiplier {multiplier}')
            ) 