from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from decimal import Decimal
from django.utils import timezone


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card (Stripe)'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('processing', 'Payment Processing'),
        ('completed', 'Payment Completed'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Payment Refunded'),
        ('partially_refunded', 'Partially Refunded'),
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
    
    # Payment fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Bank transfer reference or payment ID")
    payment_notes = models.TextField(blank=True, help_text="Additional payment information")
    
    # Refund fields
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Amount refunded")
    refund_reason = models.TextField(blank=True, help_text="Reason for refund")
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='refunds_processed')
    
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
            'card': 'Credit/Debit Card (Stripe)',
        }
        return method_names.get(self.payment_method, self.payment_method.title())
    
    def get_refundable_amount(self):
        """Get the amount that can be refunded"""
        return self.get_total_cost() - self.refund_amount
    
    def can_refund(self):
        """Check if order can be refunded"""
        return self.paid and self.payment_status in ['completed', 'partially_refunded'] and self.get_refundable_amount() > 0
    
    def process_refund(self, amount, reason, processed_by=None):
        """Process a refund for this order"""
        if not self.can_refund():
            raise ValueError("Order cannot be refunded")
        
        if amount > self.get_refundable_amount():
            raise ValueError("Refund amount exceeds refundable amount")
        
        self.refund_amount += amount
        self.refund_reason = reason
        self.refund_date = timezone.now()
        self.refund_processed_by = processed_by
        
        if self.refund_amount >= self.get_total_cost():
            self.payment_status = 'refunded'
            self.status = 'refunded'
        else:
            self.payment_status = 'partially_refunded'
        
        self.save()
        
        return True


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


class Refund(models.Model):
    """Model to track refunds"""
    REFUND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Refund {self.id} for Order {self.order.id}" 