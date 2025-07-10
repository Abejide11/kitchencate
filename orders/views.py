from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Clear the cart
            cart.clear()
            
            # Check if we should skip payment (for development)
            skip_payment = request.POST.get('skip_payment', False)
            
            if skip_payment or settings.STRIPE_SECRET_KEY == 'sk_test_your_stripe_key':
                # Skip payment processing for development
                order.paid = True
                order.save()
                messages.success(request, f'Order #{order.id} has been placed successfully! (Payment skipped for development)')
                return redirect('orders:order_success', order_id=order.id)
            
            # Set up Stripe payment
            try:
                stripe_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f'Order #{order.id}',
                            },
                            'unit_amount': int(order.get_total_cost() * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(f'/orders/success/{order.id}/'),
                    cancel_url=request.build_absolute_uri('/cart/'),
                    metadata={'order_id': order.id}
                )
                
                return redirect(stripe_session.url, code=303)
            except stripe.error.AuthenticationError:
                messages.error(request, 'Payment processing is not configured. Please set up Stripe API keys.')
                return redirect('orders:order_success', order_id=order.id)
            except Exception as e:
                messages.error(request, f'Payment error: {str(e)}')
                return redirect('orders:order_success', order_id=order.id)
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    })


@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    messages.success(request, f'Order #{order.id} has been placed successfully!')
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata']['order_id']
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.stripe_id = session['payment_intent']
        order.save()

    return HttpResponse(status=200) 