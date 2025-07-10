from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import SignUpForm, LoginForm


@login_required
def profile(request):
    user = request.user
    total_orders = user.orders.count()
    # Note: We'll use total orders as paid orders for now since there's no paid field
    paid_orders = total_orders
    
    context = {
        'total_orders': total_orders,
        'paid_orders': paid_orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def dashboard(request):
    # Get total orders count
    total_orders = request.user.orders.count()
    
    # Get paid orders count
    paid_orders = request.user.orders.filter(payment_status='completed').count()
    
    # Get last 5 orders for display
    user_orders = request.user.orders.all()[:5]
    
    context = {
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'user_orders': user_orders,
    }
    return render(request, 'accounts/dashboard.html', context) 


def login_view(request):
    if request.user.is_authenticated:
        return redirect('user:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('user:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('user:dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If you have a UserProfile model, create it here
            # UserProfile.objects.get_or_create(user=user)
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('user:dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return render(request, 'accounts/logout.html') 