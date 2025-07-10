from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Order, OrderItem, BankTransferDetails
from .email_services import send_payment_confirmation_email, send_admin_payment_notification


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['get_cost']


class BankTransferDetailsInline(admin.StackedInline):
    model = BankTransferDetails
    extra = 0
    readonly_fields = ['created', 'verified']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'total_cost_display', 
                   'payment_status', 'status', 'created', 'paid']
    list_filter = ['payment_status', 'status', 'payment_method', 'created', 'paid']
    list_editable = ['payment_status', 'status', 'paid']
    search_fields = ['id', 'user__username', 'user__email', 'first_name', 'last_name', 'email']
    readonly_fields = ['created', 'updated', 'total_cost_display']
    inlines = [OrderItemInline, BankTransferDetailsInline]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Delivery Information', {
            'fields': ('address', 'postal_code', 'city')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'paid', 'stripe_id', 
                      'payment_reference', 'payment_notes')
        }),
        ('Order Status', {
            'fields': ('status', 'created', 'updated')
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def total_cost_display(self, obj):
        return f"₦{obj.get_total_cost()}"
    total_cost_display.short_description = 'Total Cost'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(
            paid=True, 
            payment_status='completed',
            status='processing'
        )
        messages.success(request, f'{updated} order(s) marked as paid.')
        
        # Send confirmation emails
        for order in queryset:
            try:
                send_payment_confirmation_email(order)
                send_admin_payment_notification(order)
            except Exception as e:
                messages.warning(request, f'Failed to send email for order #{order.id}: {e}')
    
    mark_as_paid.short_description = "Mark selected orders as paid"
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        messages.success(request, f'{updated} order(s) marked as processing.')
    
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        messages.success(request, f'{updated} order(s) marked as shipped.')
    
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        messages.success(request, f'{updated} order(s) marked as delivered.')
    
    mark_as_delivered.short_description = "Mark selected orders as delivered"
    
    def response_change(self, request, obj):
        if "_mark-paid" in request.POST:
            obj.paid = True
            obj.payment_status = 'completed'
            obj.status = 'processing'
            obj.save()
            
            try:
                send_payment_confirmation_email(obj)
                send_admin_payment_notification(obj)
                messages.success(request, f'Order #{obj.id} marked as paid and confirmation email sent.')
            except Exception as e:
                messages.warning(request, f'Order marked as paid but failed to send email: {e}')
            
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.paid:
            return self.readonly_fields + ('paid', 'payment_status')
        return self.readonly_fields


@admin.register(BankTransferDetails)
class BankTransferDetailsAdmin(admin.ModelAdmin):
    list_display = ['order', 'bank_name', 'account_name', 'account_number', 
                   'transfer_amount', 'verified', 'created']
    list_filter = ['verified', 'bank_name', 'created']
    search_fields = ['order__id', 'account_name', 'account_number', 'reference_number']
    readonly_fields = ['created', 'order_link']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_link', 'transfer_amount')
        }),
        ('Bank Information', {
            'fields': ('bank_name', 'account_name', 'account_number', 'routing_number', 
                      'swift_code', 'iban', 'nuban')
        }),
        ('Transfer Details', {
            'fields': ('reference_number', 'transfer_date', 'receipt_image')
        }),
        ('Verification', {
            'fields': ('verified', 'notes', 'verification_notes')
        }),
        ('Timestamps', {
            'fields': ('created',)
        }),
    )
    
    actions = ['verify_transfers', 'reject_transfers']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
        return "No Order"
    order_link.short_description = 'Order'
    
    def verify_transfers(self, request, queryset):
        updated = queryset.update(verified=True)
        messages.success(request, f'{updated} bank transfer(s) marked as verified.')
        
        # Update corresponding orders
        for transfer in queryset:
            if transfer.order:
                transfer.order.paid = True
                transfer.order.payment_status = 'completed'
                transfer.order.status = 'processing'
                transfer.order.save()
                
                try:
                    send_payment_confirmation_email(transfer.order)
                    send_admin_payment_notification(transfer.order)
                except Exception as e:
                    messages.warning(request, f'Failed to send email for order #{transfer.order.id}: {e}')
    
    verify_transfers.short_description = "Verify selected bank transfers"
    
    def reject_transfers(self, request, queryset):
        updated = queryset.update(verified=False)
        messages.success(request, f'{updated} bank transfer(s) marked as rejected.')
    
    reject_transfers.short_description = "Reject selected bank transfers"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity', 'get_cost']
    list_filter = ['order__created']
    search_fields = ['order__id', 'product__name']
    readonly_fields = ['get_cost']


# Customize admin site
admin.site.site_header = "KitchenCrate Admin"
admin.site.site_title = "KitchenCrate Admin Portal"
admin.site.index_title = "Welcome to KitchenCrate Administration" 