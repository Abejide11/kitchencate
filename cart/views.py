from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from store.models import Product
from .cart import Cart


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override', False) == 'true'
    
    if product.is_available:
        cart.add(product=product, quantity=quantity, override_quantity=override)
        messages.success(request, f'{product.name} added to cart successfully!')
    else:
        messages.error(request, f'{product.name} is not available.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'message': f'{product.name} added to cart successfully!'
        })
    
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, f'{product.name} quantity updated.')
    else:
        cart.remove(product)
        messages.success(request, f'{product.name} removed from cart.')
    
    return redirect('cart:cart_detail') 