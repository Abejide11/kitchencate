from django.core.management.base import BaseCommand
from django.core.files import File
from store.models import Product
import os
from pathlib import Path
import random

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class Command(BaseCommand):
    help = 'Generate realistic product images based on product names and categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of images even if they already exist',
        )

    def handle(self, *args, **options):
        products = Product.objects.all()
        
        if not options['force']:
            products = products.filter(image='')
        
        if not products.exists():
            self.stdout.write(
                self.style.SUCCESS('All products already have images! Use --force to regenerate.')
            )
            return
        
        self.stdout.write(f'Generating images for {products.count()} products...')
        
        if not PIL_AVAILABLE:
            self.stdout.write(
                self.style.ERROR('Pillow is not installed. Please install it with: pip install Pillow')
            )
            return
        
        try:
            for product in products:
                self.generate_product_image(product)
                self.stdout.write(f'Generated image for: {product.name}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully generated images for {products.count()} products!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating images: {e}')
            )

    def generate_product_image(self, product):
        """Generate a realistic product image based on product name and category"""
        
        # Create a larger, more realistic image
        width, height = 600, 400
        img = Image.new('RGB', (width, height), color='#ffffff')
        draw = ImageDraw.Draw(img)
        
        # Get product info for customization
        product_name = product.name.lower()
        category_name = product.category.name.lower()
        
        # Define color schemes based on category
        category_colors = {
            # 'electronics': ['#2c3e50', '#3498db', '#ecf0f1', '#34495e'],
            # 'clothing': ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71'],
            # 'automotive': ['#c0392b', '#e74c3c', '#95a5a6', '#7f8c8d'],
            # Remove other unwanted categories as needed
        }
        
        # Get appropriate color scheme
        colors = category_colors.get(category_name, ['#3498db', '#2980b9', '#ecf0f1', '#34495e'])
        
        # Draw background with gradient effect
        self.draw_gradient_background(draw, width, height, colors[0], colors[1])
        
        # Draw product representation based on type
        if any(word in product_name for word in ['laptop', 'computer', 'monitor', 'webcam']):
            self.draw_electronics_device(draw, width, height, colors)
        elif any(word in product_name for word in ['headphone', 'speaker', 'audio']):
            self.draw_audio_device(draw, width, height, colors, product_name)
        elif any(word in product_name for word in ['bottle', 'water']):
            self.draw_bottle(draw, width, height, colors)
        elif any(word in product_name for word in ['cable', 'usb']):
            self.draw_cable(draw, width, height, colors)
        elif any(word in product_name for word in ['mouse', 'keyboard']):
            self.draw_computer_accessory(draw, width, height, colors, product_name)
        elif any(word in product_name for word in ['watch', 'fitness']):
            self.draw_smartwatch(draw, width, height, colors)
        elif any(word in product_name for word in ['lamp', 'light']):
            self.draw_lamp(draw, width, height, colors)
        elif any(word in product_name for word in ['stand']):
            self.draw_stand(draw, width, height, colors)
        else:
            self.draw_generic_product(draw, width, height, colors)
        
        # Add product name text
        self.add_product_text(draw, width, height, product.name, colors)
        
        # Add subtle shadow and border
        self.add_final_touches(draw, width, height)
        
        # Save the image
        image_path = f'media/products/generated_{product.slug}.png'
        img.save(image_path)
        
        # Attach to product
        with open(image_path, 'rb') as f:
            product.image.save(
                f'generated_{product.slug}.png',
                File(f),
                save=True
            )
        
        # Clean up temporary file
        os.remove(image_path)

    def draw_gradient_background(self, draw, width, height, color1, color2):
        """Draw a gradient background"""
        for y in range(height):
            ratio = y / height
            r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
            g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
            b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    def draw_electronics_device(self, draw, width, height, colors):
        """Draw a laptop or monitor"""
        # Draw device body
        device_width = width // 2
        device_height = height // 2
        x = (width - device_width) // 2
        y = (height - device_height) // 2
        
        # Main body
        draw.rectangle([x, y, x + device_width, y + device_height], 
                      fill=colors[2], outline=colors[3], width=3)
        
        # Screen
        screen_margin = 20
        draw.rectangle([x + screen_margin, y + screen_margin, 
                       x + device_width - screen_margin, y + device_height - screen_margin], 
                      fill=colors[0])
        
        # Add some screen content
        draw.rectangle([x + screen_margin + 30, y + screen_margin + 30, 
                       x + device_width - screen_margin - 30, y + device_height - screen_margin - 30], 
                      fill=colors[1])

    def draw_audio_device(self, draw, width, height, colors, product_name=''):
        """Draw headphones or speaker"""
        center_x, center_y = width // 2, height // 2
        
        # Draw headphones
        if 'headphone' in product_name.lower():
            # Left ear cup
            draw.ellipse([center_x - 80, center_y - 40, center_x - 20, center_y + 40], 
                        fill=colors[0], outline=colors[3], width=2)
            # Right ear cup
            draw.ellipse([center_x + 20, center_y - 40, center_x + 80, center_y + 40], 
                        fill=colors[0], outline=colors[3], width=2)
            # Headband
            draw.arc([center_x - 60, center_y - 60, center_x + 60, center_y - 20], 
                    0, 180, fill=colors[3], width=4)
        else:
            # Draw speaker
            draw.ellipse([center_x - 60, center_y - 60, center_x + 60, center_y + 60], 
                        fill=colors[0], outline=colors[3], width=3)
            # Speaker cone
            draw.ellipse([center_x - 40, center_y - 40, center_x + 40, center_y + 40], 
                        fill=colors[1])

    def draw_bottle(self, draw, width, height, colors):
        """Draw a water bottle"""
        center_x, center_y = width // 2, height // 2
        
        # Bottle body
        draw.rectangle([center_x - 30, center_y - 60, center_x + 30, center_y + 60], 
                      fill=colors[1], outline=colors[3], width=2)
        
        # Bottle neck
        draw.rectangle([center_x - 15, center_y - 80, center_x + 15, center_y - 60], 
                      fill=colors[1], outline=colors[3], width=2)
        
        # Cap
        draw.ellipse([center_x - 20, center_y - 90, center_x + 20, center_y - 80], 
                    fill=colors[0])

    def draw_cable(self, draw, width, height, colors):
        """Draw a USB cable"""
        # Cable body
        for i in range(0, width, 20):
            y_offset = 10 * (i // 40) % 20
            draw.line([(i, height//2 - 30 + y_offset), (i + 15, height//2 - 30 + y_offset)], 
                     fill=colors[0], width=8)
        
        # Connectors
        draw.rectangle([50, height//2 - 40, 80, height//2 - 20], 
                      fill=colors[1], outline=colors[3], width=2)
        draw.rectangle([width - 80, height//2 - 40, width - 50, height//2 - 20], 
                      fill=colors[1], outline=colors[3], width=2)

    def draw_computer_accessory(self, draw, width, height, colors, product_name=''):
        """Draw a mouse or keyboard"""
        center_x, center_y = width // 2, height // 2
        
        if 'mouse' in product_name.lower():
            # Mouse shape
            draw.ellipse([center_x - 40, center_y - 25, center_x + 40, center_y + 25], 
                        fill=colors[0], outline=colors[3], width=2)
            # Scroll wheel
            draw.ellipse([center_x - 8, center_y - 8, center_x + 8, center_y + 8], 
                        fill=colors[1])
        else:
            # Keyboard
            draw.rectangle([center_x - 80, center_y - 20, center_x + 80, center_y + 20], 
                          fill=colors[0], outline=colors[3], width=2)
            # Keys
            for i in range(-6, 7):
                for j in range(-2, 3):
                    draw.rectangle([center_x + i*20 - 8, center_y + j*12 - 5, 
                                   center_x + i*20 + 8, center_y + j*12 + 5], 
                                  fill=colors[1])

    def draw_smartwatch(self, draw, width, height, colors):
        """Draw a smartwatch"""
        center_x, center_y = width // 2, height // 2
        
        # Watch body
        draw.ellipse([center_x - 50, center_y - 50, center_x + 50, center_y + 50], 
                    fill=colors[0], outline=colors[3], width=3)
        
        # Screen
        draw.ellipse([center_x - 40, center_y - 40, center_x + 40, center_y + 40], 
                    fill=colors[1])
        
        # Watch band
        draw.rectangle([center_x - 60, center_y - 10, center_x - 50, center_y + 10], 
                      fill=colors[2])
        draw.rectangle([center_x + 50, center_y - 10, center_x + 60, center_y + 10], 
                      fill=colors[2])

    def draw_lamp(self, draw, width, height, colors):
        """Draw a desk lamp"""
        center_x, center_y = width // 2, height // 2
        
        # Base
        draw.rectangle([center_x - 40, center_y + 40, center_x + 40, center_y + 60], 
                      fill=colors[0], outline=colors[3], width=2)
        
        # Stand
        draw.line([(center_x, center_y + 40), (center_x, center_y - 20)], 
                 fill=colors[0], width=8)
        
        # Lamp head
        draw.ellipse([center_x - 30, center_y - 50, center_x + 30, center_y - 20], 
                    fill=colors[1], outline=colors[3], width=2)
        
        # Light beam
        draw.polygon([(center_x - 20, center_y - 20), (center_x - 40, center_y + 20), 
                     (center_x + 40, center_y + 20), (center_x + 20, center_y - 20)], 
                    fill=colors[2])

    def draw_stand(self, draw, width, height, colors):
        """Draw a monitor or laptop stand"""
        center_x, center_y = width // 2, height // 2
        
        # Stand base
        draw.rectangle([center_x - 60, center_y + 20, center_x + 60, center_y + 40], 
                      fill=colors[0], outline=colors[3], width=2)
        
        # Stand arm
        draw.rectangle([center_x - 10, center_y - 40, center_x + 10, center_y + 20], 
                      fill=colors[0], outline=colors[3], width=2)
        
        # Platform
        draw.rectangle([center_x - 50, center_y - 60, center_x + 50, center_y - 40], 
                      fill=colors[1], outline=colors[3], width=2)

    def draw_generic_product(self, draw, width, height, colors):
        """Draw a generic product box"""
        center_x, center_y = width // 2, height // 2
        
        # Product box
        draw.rectangle([center_x - 60, center_y - 40, center_x + 60, center_y + 40], 
                      fill=colors[0], outline=colors[3], width=3)
        
        # Add some details
        draw.rectangle([center_x - 50, center_y - 30, center_x + 50, center_y + 30], 
                      fill=colors[1])
        
        # Product lines
        for i in range(3):
            y = center_y - 15 + i * 15
            draw.line([(center_x - 40, y), (center_x + 40, y)], fill=colors[2], width=2)

    def add_product_text(self, draw, width, height, product_name, colors):
        """Add product name text"""
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Split product name into words
        words = product_name.split()
        if len(words) > 3:
            words = words[:3]  # Limit to 3 words
        
        text = ' '.join(words).upper()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = height - text_height - 20
        
        # Draw text with outline
        draw.text((x, y), text, fill=colors[3], font=font)

    def add_final_touches(self, draw, width, height):
        """Add shadows and final touches"""
        # Add subtle border
        draw.rectangle([0, 0, width-1, height-1], outline='#cccccc', width=2)
        
        # Add corner highlights
        draw.line([(0, 0), (20, 0)], fill='#ffffff', width=3)
        draw.line([(0, 0), (0, 20)], fill='#ffffff', width=3) 