from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import SignUpForm, LoginForm, ProfileUpdateForm


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


@login_required
def profile_update(request):
    """Update user profile information"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_update.html', {'form': form})


def password_reset(request):
    """Password reset request form"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate password reset email
                subject = 'KitchenCrate - Password Reset Request'
                email_template_name = 'accounts/password_reset_email.html'
                c = {
                    'email': user.email,
                    'domain': request.get_host(),
                    'site_name': 'KitchenCrate',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http',
                }
                email = render_to_string(email_template_name, c)
                send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                return redirect('user:password_reset_done')
            except User.DoesNotExist:
                # Don't reveal if email exists or not
                return redirect('user:password_reset_done')
    else:
        form = PasswordResetForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_done(request):
    """Password reset email sent confirmation"""
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation and new password form"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('user:password_reset_complete')
        else:
            form = SetPasswordForm(user)
    else:
        form = None
        messages.error(request, 'The password reset link is invalid or has expired.')

    return render(request, 'accounts/password_reset_confirm.html', {'form': form})


def password_reset_complete(request):
    """Password reset complete confirmation"""
    return render(request, 'accounts/password_reset_complete.html') 