from django.contrib import admin
from .models import Order, OrderItem, BankTransferDetails


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['price']


class BankTransferDetailsInline(admin.StackedInline):
    model = BankTransferDetails
    extra = 0
    readonly_fields = ['transfer_amount', 'created']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'email', 'payment_method_display', 
        'payment_status_display', 'total_cost_display', 'created', 'status'
    ]
    list_filter = [
        'payment_method', 'payment_status', 'status', 'created', 'paid'
    ]
    list_editable = ['status']
    search_fields = ['id', 'user__username', 'user__email', 'email', 'first_name', 'last_name']
    readonly_fields = ['id', 'created', 'updated', 'total_cost_display']
    inlines = [OrderItemInline, BankTransferDetailsInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'created', 'updated', 'status')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Delivery Information', {
            'fields': ('address', 'postal_code', 'city', 'state')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'paid', 'stripe_id', 'payment_reference', 'payment_notes')
        }),
        ('Order Summary', {
            'fields': ('total_cost_display',),
            'classes': ('collapse',)
        }),
    )
    
    def payment_method_display(self, obj):
        """Display payment method with icon"""
        icons = {
            'card': '💳',
            'bank_transfer': '🏦',
    
            'ussd': '📱',
            'mobile_money': '📲',
            
            'apple_pay': '🍎',
            'google_pay': '🤖'
        }
        icon = icons.get(obj.payment_method, '💰')
        return f"{icon} {obj.get_payment_method_display()}"
    payment_method_display.short_description = 'Payment Method'
    
    def payment_status_display(self, obj):
        """Display payment status with color coding"""
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'blue',
            'cancelled': 'gray'
        }
        color = colors.get(obj.payment_status, 'black')
        return f"<span style=\"color: {color}; font-weight: bold;\">{obj.get_payment_status_display()}</span>"
    payment_status_display.short_description = 'Payment Status'
    
    def total_cost_display(self, obj):
        """Display total cost with currency"""
        return f"₦{obj.get_total_cost():,.2f}"
    total_cost_display.short_description = 'Total Cost'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')
    
    actions = ['mark_as_paid', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_paid(self, request, queryset):
        """Mark selected orders as paid"""
        updated = queryset.update(paid=True, payment_status='completed')
        self.message_user(request, f'{updated} orders marked as paid.')
    mark_as_paid.short_description = "Mark selected orders as paid"
    
    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing"""
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        """Mark selected orders as shipped"""
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        """Mark selected orders as delivered"""
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"


@admin.register(BankTransferDetails)
class BankTransferDetailsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'bank_name', 'account_name', 'account_number', 
        'transfer_amount', 'reference_number', 'created', 'verified'
    ]
    list_filter = ['bank_name', 'verified', 'created']
    search_fields = ['order__id', 'account_name', 'account_number', 'reference_number']
    readonly_fields = ['order', 'transfer_amount', 'created']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'transfer_amount', 'created')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_name', 'account_number', 'nuban')
        }),
        ('Transfer Information', {
            'fields': ('reference_number', 'transfer_date', 'receipt_image')
        }),
        ('Verification', {
            'fields': ('verified', 'verification_notes')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('order')
    
    actions = ['mark_as_verified', 'mark_as_unverified']
    
    def mark_as_verified(self, request, queryset):
        """Mark selected transfers as verified"""
        updated = queryset.update(verified=True)
        # Update corresponding orders
        for transfer in queryset:
            if transfer.order:
                transfer.order.payment_status = 'completed'
                transfer.order.paid = True
                transfer.order.save()
        self.message_user(request, f'{updated} transfers marked as verified.')
    mark_as_verified.short_description = "Mark selected transfers as verified"
    
    def mark_as_unverified(self, request, queryset):
        """Mark selected transfers as unverified"""
        updated = queryset.update(verified=False)
        self.message_user(request, f'{updated} transfers marked as unverified.')
    mark_as_unverified.short_description = "Mark selected transfers as unverified"


# Customize admin site
admin.site.site_header = "KitchenCrate Admin"
admin.site.site_title = "KitchenCrate Admin Portal"
admin.site.index_title = "Welcome to KitchenCrate Administration" 