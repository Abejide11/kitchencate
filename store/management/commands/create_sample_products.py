from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Category, Product
import random


class Command(BaseCommand):
    help = 'Create sample products for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of products to create'
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=5,
            help='Number of categories to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        categories_count = options['categories']
        
        # Sample data
        category_names = [
            'Sports', 'Toys', 'Health', 'Food & Beverages', 'Cakes & pastries'
        ]
        
        product_names = [
            'Stainless Steel Water Bottle', 'LED Desk Lamp', 'Wireless Bluetooth Speaker',
            'Portable Power Bank', 'Smartphone Case', 'Laptop Stand', 'USB-C Cable',
            'Wireless Mouse', 'Mechanical Keyboard', 'Gaming Headset', 'Webcam HD',
            'External Hard Drive', 'Tablet Stand', 'Phone Mount', 'Cable Organizer',
            'Desk Mat', 'Monitor Stand'
        ]
        
        descriptions = [
            'High-quality product with excellent features and durability.',
            'Premium design with advanced technology for optimal performance.',
            'Eco-friendly materials with modern styling and comfort.',
            'Innovative design that combines functionality with aesthetics.',
            'Professional grade equipment suitable for various applications.',
            'User-friendly interface with intuitive controls and settings.',
            'Compact and portable design perfect for on-the-go use.',
            'Versatile product that adapts to different environments.',
            'Energy-efficient solution with long-lasting performance.',
            'Cost-effective option without compromising on quality.'
        ]
        
        # Create categories
        categories = []
        for i in range(min(categories_count, len(category_names))):
            category, created = Category.objects.get_or_create(
                name=category_names[i],
                defaults={
                    'slug': category_names[i].lower().replace(' ', '-'),
                    'description': f'Premium {category_names[i].lower()} products for discerning customers.'
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
        
        # Create products
        for i in range(count):
            category = random.choice(categories)
            name = random.choice(product_names)
            description = random.choice(descriptions)
            
            # Generate unique name if needed
            base_name = name
            counter = 1
            while Product.objects.filter(name=name).exists():
                name = f"{base_name} {counter}"
                counter += 1
            
            product = Product.objects.create(
                name=name,
                slug=name.lower().replace(' ', '-').replace('&', 'and'),
                category=category,
                description=description,
                price=round(random.uniform(10.0, 500.0), 2),
                stock=random.randint(0, 100),
                available=random.choice([True, True, True, False]),  # 75% chance of being available
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created product: {product.name} - ${product.price}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} products in {len(categories)} categories')
        ) 