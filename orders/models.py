from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('ussd', 'USSD Payment'),
        ('mobile_money', 'Mobile Money'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('processing', 'Payment Processing'),
        ('completed', 'Payment Completed'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Payment Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_id = models.CharField(max_length=250, blank=True)
    
    # New payment fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Bank transfer reference or payment ID")
    payment_notes = models.TextField(blank=True, help_text="Additional payment information")
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def get_payment_method_display_name(self):
        """Get a user-friendly payment method name"""
        method_names = {
            'card': 'Credit/Debit Card',
            'bank_transfer': 'Bank Transfer',
            'apple_pay': 'Apple Pay',
            'google_pay': 'Google Pay',
            'ussd': 'USSD Payment',
            'mobile_money': 'Mobile Money',
        }
        return method_names.get(self.payment_method, self.payment_method.title())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity


class BankTransferDetails(models.Model):
    """Model to store bank transfer information"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='bank_transfer')
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=20, blank=True, help_text="Sort Code (for UK) or Routing Number (for US)")
    swift_code = models.CharField(max_length=20, blank=True, help_text="SWIFT/BIC code for international transfers")
    iban = models.CharField(max_length=50, blank=True, help_text="IBAN for international transfers")
    nuban = models.CharField(max_length=20, blank=True, help_text="NUBAN (Nigerian Uniform Bank Account Number)")
    reference_number = models.CharField(max_length=50, blank=True)
    transfer_date = models.DateField(null=True, blank=True)
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_image = models.ImageField(upload_to='bank_transfers/', blank=True)
    notes = models.TextField(blank=True)
    verification_notes = models.TextField(blank=True, help_text="Admin notes for verification process")
    created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Bank Transfer for Order {self.order.id}" 