from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
import json
from .models import Order, OrderItem, BankTransferDetails
from .forms import OrderCreateForm, BankTransferForm
from .payment_services import get_payment_service
from .email_services import send_payment_confirmation_email, send_order_created_email, send_payment_pending_email, send_admin_payment_notification
from cart.cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from store.models import Product
import stripe


@login_required
def payment_dashboard(request):
    """Payment dashboard for users to view their payment history and status"""
    
    # Get user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created')
    
    # Calculate payment statistics
    total_orders = orders.count()
    total_spent = sum(order.get_total_cost() for order in orders)
    completed_payments = orders.filter(payment_status='completed').count()
    pending_payments = orders.filter(payment_status='pending').count()
    
    # Calculate percentages for progress bars
    completed_percentage = (completed_payments / total_orders * 100) if total_orders > 0 else 0
    pending_percentage = (pending_payments / total_orders * 100) if total_orders > 0 else 0
    
    # Payment method breakdown
    payment_methods = {}
    for order in orders:
        method = order.get_payment_method_display()
        if method not in payment_methods:
            payment_methods[method] = {'count': 0, 'amount': 0}
        payment_methods[method]['count'] += 1
        payment_methods[method]['amount'] += order.get_total_cost()
    
    # Calculate percentage for each payment method
    for method_data in payment_methods.values():
        method_data['percentage'] = (method_data['amount'] / total_spent * 100) if total_spent > 0 else 0
    
    # Recent orders (last 5)
    recent_orders = orders[:5]
    
    # Pending payments
    pending_orders = orders.filter(payment_status='pending')[:3]
    
    # Payment status distribution
    status_distribution = {
        'completed': orders.filter(payment_status='completed').count(),
        'pending': orders.filter(payment_status='pending').count(),
        'failed': orders.filter(payment_status='failed').count(),
        'processing': orders.filter(payment_status='processing').count(),
    }
    
    context = {
        'total_orders': total_orders,
        'total_spent': total_spent,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'completed_percentage': completed_percentage,
        'pending_percentage': pending_percentage,
        'payment_methods': payment_methods,
        'recent_orders': recent_orders,
        'pending_orders': pending_orders,
        'status_distribution': status_distribution,
    }
    
    return render(request, 'orders/payment_dashboard.html', context)


@login_required
def order_create(request):
    cart = Cart(request)
    
    # Check if cart is empty
    if not cart:
        messages.warning(request, 'Your cart is empty. Please add some items before checkout.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.payment_method = form.cleaned_data['payment_method']
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Clear the cart
            cart.clear()
            
            # Notify admin of new order
            send_admin_payment_notification(order)
            
            # Process payment with Stripe
            payment_service = get_payment_service(order)
            result = payment_service.process_payment(request)
            if result['success']:
                order.payment_reference = result.get('payment_reference', f'STRIPE-{order.id}')
                order.payment_status = 'processing'
                order.payment_notes = f'Stripe payment initiated. Reference: {result.get("payment_reference", "")}'
                order.save()
                return redirect(result['redirect_url'])
            else:
                messages.error(request, 'Stripe payment error.')
                return redirect('orders:order_create')
    else:
        # Pre-fill form with user data if available
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name or '',
                'last_name': request.user.last_name or '',
                'email': request.user.email or '',
            }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form,
        'stripe_pk': settings.STRIPE_PUBLISHABLE_KEY,
    })


def process_flutterwave_payment(request, order, payment_method):
    """Process Flutterwave payment with different payment methods"""
    # Check if Flutterwave is properly configured
    if settings.FLUTTERWAVE_SECRET_KEY == 'FLWSECK_TEST_your_flutterwave_secret_key':
        messages.error(request, 'Flutterwave payment processing is not configured. Please contact support.')
        return redirect('orders:order_success', order_id=order.id)
    
    # Use payment service
    payment_service = get_payment_service(order, payment_method)
    result = payment_service.process_payment(request, payment_method)
    
    if result['success']:
        # Store payment reference
        order.payment_reference = result.get('payment_reference', f'FLW-{order.id}')
        order.payment_status = 'processing'
        order.payment_notes = f'Flutterwave payment initiated. Reference: {result.get("payment_reference", "")}'
        order.save()
        
        return redirect(result['redirect_url'], code=303)
    else:
        messages.error(request, f'Flutterwave payment error: {result["error"]}')
        return redirect('orders:order_success', order_id=order.id)








@login_required
def ussd_payment(request, order_id):
    """Handle USSD payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment_service = get_payment_service(order, 'ussd')
    
    if request.method == 'POST':
        bank_code = request.POST.get('bank_code')
        account_number = request.POST.get('account_number')
        
        if bank_code and account_number:
            ussd_code = payment_service.generate_ussd_code(bank_code, account_number)
            if ussd_code:
                # Store payment details
                order.payment_reference = f"USSD-{order.id}"
                order.payment_status = 'pending'
                order.payment_notes = f'USSD payment pending. Code: {ussd_code}'
                order.save()
                
                # Send pending payment email
                try:
                    send_payment_pending_email(order)
                except Exception as e:
                    messages.warning(request, f'USSD payment initiated but failed to send email: {e}')
                
                messages.success(request, f'USSD payment initiated for Order #{order.id}. Please complete the payment using the provided code.')
                return redirect('orders:order_success', order_id=order.id)
    
    payment_info = payment_service.get_payment_instructions()
    
    return render(request, 'orders/ussd_payment.html', {
        'order': order,
        'payment_info': payment_info
    })


@login_required
def mobile_money_payment(request, order_id):
    """Handle Mobile Money payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment_service = get_payment_service(order, 'mobile_money')
    
    if request.method == 'POST':
        provider = request.POST.get('provider')
        phone_number = request.POST.get('phone_number')
        
        if provider and phone_number:
            payment_code = payment_service.generate_payment_code(provider, phone_number)
            if payment_code:
                # Store payment details
                order.payment_reference = f"MOBILE-{order.id}"
                order.payment_status = 'pending'
                order.payment_notes = f'Mobile money payment pending. Code: {payment_code}'
                order.save()
                
                # Send pending payment email
                try:
                    send_payment_pending_email(order)
                except Exception as e:
                    messages.warning(request, f'Mobile money payment initiated but failed to send email: {e}')
                
                messages.success(request, f'Mobile money payment initiated for Order #{order.id}. Please complete the payment using the provided code.')
                return redirect('orders:order_success', order_id=order.id)
    
    return render(request, 'orders/mobile_money_payment.html', {
        'order': order,
        'providers': payment_service.providers
    })


@login_required
def bank_transfer_details(request, order_id):
    """Handle bank transfer payment details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        form = BankTransferForm(request.POST, request.FILES)
        if form.is_valid():
            bank_transfer = form.save(commit=False)
            bank_transfer.order = order
            bank_transfer.transfer_amount = order.get_total_cost()
            bank_transfer.save()
            
            # Update order with bank transfer reference
            order.payment_reference = bank_transfer.reference_number
            order.payment_status = 'pending'
            order.payment_notes = f'Bank transfer pending verification. Reference: {bank_transfer.reference_number}'
            order.save()
            
            # Send pending payment email
            try:
                send_payment_pending_email(order)
            except Exception as e:
                messages.warning(request, f'Bank transfer submitted but failed to send email: {e}')
            
            messages.success(request, f'Bank transfer details submitted for Order #{order.id}. We will verify your payment and confirm your order.')
            return redirect('orders:order_success', order_id=order.id)
    else:
        form = BankTransferForm(initial={'transfer_amount': order.get_total_cost()})
    
    return render(request, 'orders/bank_transfer_details.html', {
        'order': order,
        'form': form
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.paid or order.payment_status == 'completed':
        messages.success(request, f'Thank you! Your order #{order.id} has been confirmed and payment received.')
    elif order.payment_method == 'bank_transfer':
        messages.info(request, f'Order #{order.id} created successfully! We will verify your bank transfer and confirm your order.')

    elif order.payment_method == 'ussd':
        messages.info(request, f'Order #{order.id} created successfully! Please complete your USSD payment.')
    elif order.payment_method == 'mobile_money':
        messages.info(request, f'Order #{order.id} created successfully! Please complete your mobile money payment.')
    else:
        messages.warning(request, f'Order #{order.id} created but payment is pending. You will receive an email confirmation once payment is processed.')
    
    return render(request, 'orders/order_success.html', {
        'order': order,
        'stripe_pk': settings.STRIPE_PUBLISHABLE_KEY,
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@csrf_exempt
@require_POST
def flutterwave_webhook(request):
    """Handle Flutterwave webhooks"""
    try:
        # Get the webhook payload
        payload = json.loads(request.body)
        
        # Get the order from metadata
        order_id = payload.get('data', {}).get('meta', {}).get('order_id')
        if not order_id:
            return HttpResponse(status=400)
        
        # Get the order
        order = Order.objects.get(id=order_id)
        
        # Process the webhook using Flutterwave service
        from .flutterwave_services import get_flutterwave_service
        flutterwave_service = get_flutterwave_service(order)
        result = flutterwave_service.process_webhook(payload)
        
        if result['success']:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
            
    except Order.DoesNotExist:
        return HttpResponse(status=404)
    except Exception as e:
        print(f"Flutterwave webhook error: {e}")
        return HttpResponse(status=500)


# Optional: Add a view to handle payment status checks
@login_required
def check_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.stripe_id:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(order.stripe_id)
            return JsonResponse({
                'status': payment_intent.status,
                'paid': order.paid
            })
        except stripe.error.StripeError:
            return JsonResponse({'error': 'Unable to retrieve payment status'}, status=400)
    
    return JsonResponse({'paid': order.paid}) 


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata'].get('order_id')
        try:
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.payment_status = 'completed'
            order.save()
            send_payment_confirmation_email(order)
            send_admin_payment_notification(order)
        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200) 