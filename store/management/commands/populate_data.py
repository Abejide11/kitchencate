from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = 'Populate the database with sample categories and products'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create categories
        categories_data = [
            {
                'name': 'Rice',
                'description': 'Delicious rice dishes from around the world.'
            },
            {
                'name': 'Seafood',
                'description': 'Fresh and tasty seafood meals.'
            },
            {
                'name': 'Swallow',
                'description': 'Traditional swallow dishes.'
            },
            {
                'name': 'Soup',
                'description': 'Hearty and flavorful soups.'
            },
            {
                'name': 'Pasta',
                'description': 'Classic and modern pasta recipes.'
            },
            {
                'name': 'Assorted Meat/Snack',
                'description': 'A variety of meats and snacks.'
            },
            {
                'name': 'Cakes & pastries',
                'description': 'Delicious cakes and pastries for every occasion.'
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create products
        products_data = [
            # Rice
            {
                'name': 'Jollof Rice',
                'category': 'Rice',
                'description': 'Classic West African jollof rice with tomato and spices.',
                'price': 8.99,
                'stock': 50
            },
            {
                'name': 'Fried Rice',
                'category': 'Rice',
                'description': 'Nigerian-style fried rice with vegetables and chicken.',
                'price': 9.99,
                'stock': 40
            },
            # Seafood
            {
                'name': 'Grilled Fish',
                'category': 'Seafood',
                'description': 'Freshly grilled tilapia with pepper sauce.',
                'price': 12.99,
                'stock': 30
            },
            {
                'name': 'Seafood Okra',
                'category': 'Seafood',
                'description': 'Okra soup loaded with prawns, crab, and fish.',
                'price': 13.99,
                'stock': 25
            },
            # Swallow
            {
                'name': 'Pounded Yam',
                'category': 'Swallow',
                'description': 'Smooth pounded yam served with your choice of soup.',
                'price': 6.99,
                'stock': 60
            },
            {
                'name': 'Eba',
                'category': 'Swallow',
                'description': 'Cassava-based swallow, perfect with any soup.',
                'price': 5.99,
                'stock': 70
            },
            # Soup
            {
                'name': 'Egusi Soup',
                'category': 'Soup',
                'description': 'Melon seed soup with assorted meats and vegetables.',
                'price': 10.99,
                'stock': 35
            },
            {
                'name': 'Afang Soup',
                'category': 'Soup',
                'description': 'Rich vegetable soup with periwinkle and beef.',
                'price': 11.99,
                'stock': 30
            },
            # Pasta
            {
                'name': 'Spaghetti Bolognese',
                'category': 'Pasta',
                'description': 'Spaghetti with rich tomato and beef sauce.',
                'price': 9.49,
                'stock': 40
            },
            {
                'name': 'Pasta Alfredo',
                'category': 'Pasta',
                'description': 'Creamy Alfredo pasta with chicken and mushrooms.',
                'price': 10.49,
                'stock': 35
            },
            # Assorted Meat/Snack
            {
                'name': 'Peppered Gizzard',
                'category': 'Assorted Meat/Snack',
                'description': 'Spicy grilled gizzard, a perfect snack.',
                'price': 7.99,
                'stock': 50
            },
            {
                'name': 'Meat Pie',
                'category': 'Assorted Meat/Snack',
                'description': 'Flaky pastry filled with minced meat and vegetables.',
                'price': 3.99,
                'stock': 100
            }
        ]

        for product_data in products_data:
            category = categories[product_data['category']]
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                category=category,
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock']
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        ) 