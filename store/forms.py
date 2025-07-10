from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'category', 'description', 'price', 'stock', 'available', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto-generated'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Product Name',
            'slug': 'URL Slug',
            'category': 'Category',
            'description': 'Description',
            'price': 'Price (₦)',
            'stock': 'Stock Quantity',
            'available': 'Available for Purchase',
            'image': 'Product Image',
        }
        help_texts = {
            'slug': 'Leave empty to auto-generate from product name',
            'price': 'Enter price in Naira (e.g., 25000.00)',
            'stock': 'Number of items available in stock',
            'available': 'Check if product should be visible to customers',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto-generated'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter category description'}),
        }
        labels = {
            'name': 'Category Name',
            'slug': 'URL Slug',
            'description': 'Description',
        }
        help_texts = {
            'slug': 'Leave empty to auto-generate from category name',
        } 