from django.core.management.base import BaseCommand
from django.core.files import File
from store.models import Product
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Add sample images to products that don\'t have images'

    def handle(self, *args, **options):
        products_without_images = Product.objects.filter(image='')
        
        if not products_without_images.exists():
            self.stdout.write(
                self.style.SUCCESS('All products already have images!')
            )
            return
        
        self.stdout.write(f'Found {products_without_images.count()} products without images')
        
        # Create a sample image using a simple colored rectangle
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple sample image
            img = Image.new('RGB', (400, 300), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # Draw a simple border
            draw.rectangle([0, 0, 399, 299], outline='#dee2e6', width=2)
            
            # Add text
            draw.text((200, 150), "Sample\nProduct\nImage", fill='#6c757d', anchor='mm')
            
            # Save the sample image
            sample_image_path = Path('media/products/sample_product.png')
            img.save(sample_image_path)
            
            # Add the sample image to products without images
            for product in products_without_images:
                with open(sample_image_path, 'rb') as f:
                    product.image.save(
                        f'sample_{product.slug}.png',
                        File(f),
                        save=True
                    )
                self.stdout.write(f'Added sample image to: {product.name}')
            
            # Clean up the temporary file
            os.remove(sample_image_path)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully added sample images to {products_without_images.count()} products!')
            )
            
        except ImportError:
            self.stdout.write(
                self.style.ERROR('Pillow is not installed. Please install it with: pip install Pillow')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample images: {e}')
            ) 