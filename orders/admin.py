from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'paid', 'status', 'created']
    list_filter = ['paid', 'status', 'created']
    inlines = [OrderItemInline]
    search_fields = ['first_name', 'last_name', 'email']
    list_per_page = 20 