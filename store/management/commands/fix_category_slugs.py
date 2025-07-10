from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category


class Command(BaseCommand):
    help = 'Fix category slugs that contain invalid characters'

    def handle(self, *args, **options):
        self.stdout.write('Fixing category slugs...')
        
        # Get all categories
        categories = Category.objects.all()
        
        for category in categories:
            # Generate a new slug
            new_slug = slugify(category.name)
            
            # Check if the slug has changed
            if category.slug != new_slug:
                old_slug = category.slug
                category.slug = new_slug
                category.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Fixed slug for "{category.name}": {old_slug} -> {new_slug}')
                )
            else:
                self.stdout.write(f'Slug for "{category.name}" is already correct: {category.slug}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully fixed all category slugs!')
        ) 