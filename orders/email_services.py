from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User


def send_payment_confirmation_email(order):
    """Send payment confirmation email to customer"""
    subject = f'Payment Confirmed - Order #{order.id}'
    
    context = {
        'order': order,
        'user': order.user,
        'total_cost': order.get_total_cost(),
        'payment_method': order.get_payment_method_display_name(),
    }
    
    html_message = render_to_string('orders/emails/payment_confirmation.html', context)
    plain_message = render_to_string('orders/emails/payment_confirmation.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_order_created_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmed - Order #{order.id}'
    
    context = {
        'order': order,
        'user': order.user,
        'total_cost': order.get_total_cost(),
        'payment_method': order.get_payment_method_display_name(),
    }
    
    html_message = render_to_string('orders/emails/order_created.html', context)
    plain_message = render_to_string('orders/emails/order_created.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_payment_pending_email(order):
    """Send payment pending email to customer"""
    subject = f'Payment Pending - Order #{order.id}'
    
    context = {
        'order': order,
        'user': order.user,
        'total_cost': order.get_total_cost(),
        'payment_method': order.get_payment_method_display_name(),
    }
    
    html_message = render_to_string('orders/emails/payment_pending.html', context)
    plain_message = render_to_string('orders/emails/payment_pending.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_payment_failed_email(order, error_message=""):
    """Send payment failed email to customer"""
    subject = f'Payment Failed - Order #{order.id}'
    
    context = {
        'order': order,
        'user': order.user,
        'total_cost': order.get_total_cost(),
        'payment_method': order.get_payment_method_display_name(),
        'error_message': error_message,
    }
    
    html_message = render_to_string('orders/emails/payment_failed.html', context)
    plain_message = render_to_string('orders/emails/payment_failed.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_admin_payment_notification(order):
    """Send notification to admin about new payment"""
    subject = f'New Payment Received - Order #{order.id}'
    
    context = {
        'order': order,
        'user': order.user,
        'total_cost': order.get_total_cost(),
        'payment_method': order.get_payment_method_display_name(),
    }
    
    html_message = render_to_string('orders/emails/admin_payment_notification.html', context)
    plain_message = render_to_string('orders/emails/admin_payment_notification.txt', context)
    
    # Send to admin email (you can configure this in settings)
    admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
        html_message=html_message,
        fail_silently=False,
    ) 