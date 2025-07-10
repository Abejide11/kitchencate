from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'image_preview', 'available', 'created_at']
    list_filter = ['available', 'created_at', 'category']
    list_editable = ['price', 'stock', 'available']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'available')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Image'
    
    actions = ['make_available', 'make_unavailable', 'update_stock']
    
    def make_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(request, f'{updated} products marked as available.')
    make_available.short_description = "Mark selected products as available"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(request, f'{updated} products marked as unavailable.')
    make_unavailable.short_description = "Mark selected products as unavailable"
    
    def update_stock(self, request, queryset):
        # This is a placeholder for bulk stock update
        self.message_user(request, f'Stock update feature coming soon.')
    update_stock.short_description = "Update stock for selected products" 