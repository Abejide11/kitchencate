from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('dashboard/', views.payment_dashboard, name='payment_dashboard'),
    path('create/', views.order_create, name='order_create'),
    path('created/<int:order_id>/', views.order_success, name='order_success'),
    path('list/', views.order_list, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('bank-transfer/<int:order_id>/', views.bank_transfer_details, name='bank_transfer_details'),
    path('ussd-payment/<int:order_id>/', views.ussd_payment, name='ussd_payment'),
    path('mobile-money-payment/<int:order_id>/', views.mobile_money_payment, name='mobile_money_payment'),

    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('check-payment/<int:order_id>/', views.check_payment_status, name='check_payment_status'),
] 