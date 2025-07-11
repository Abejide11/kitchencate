from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from .models import Category, Product
from .forms import ProductForm, CategoryForm
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from django.conf import settings
from orders.models import Order, OrderItem

@login_required
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == '-price':
        products = products.order_by('-price')
    elif sort_by == '-created_at':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 9)  # Show 9 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_products': paginator.count,
    }
    return render(request, 'store/product_list.html', context)

@login_required
def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/category_detail.html', context)


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def require_admin_password(view_func):
    """Decorator to require admin password verification"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_password_verified', False):
            return redirect('store:admin_password_check')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_password_check(request):
    """Check for admin password before allowing access to admin dashboard"""
    # Check if admin password is already verified in session
    if request.session.get('admin_password_verified', False):
        return redirect('store:admin_dashboard')
    
    if request.method == 'POST':
        password = request.POST.get('admin_password')
        # You can set this password in your Django settings or use a default
        admin_password = getattr(settings, 'ADMIN_DASHBOARD_PASSWORD', 'admin123')
        
        if password == admin_password:
            request.session['admin_password_verified'] = True
            messages.success(request, 'Admin access granted!')
            return redirect('store:admin_dashboard')
        else:
            messages.error(request, 'Invalid admin password!')
    
    return render(request, 'store/admin_password.html', {'admin_dashboard': True})


def admin_logout(request):
    """Logout from admin dashboard by clearing admin password session"""
    if 'admin_password_verified' in request.session:
        del request.session['admin_password_verified']
        messages.success(request, 'You have been logged out from admin dashboard.')
    return redirect('store:admin_password_check')


def admin_dashboard(request):
    """Comprehensive admin dashboard with product and category management"""
    print(f"DEBUG: Admin password verified: {request.session.get('admin_password_verified', False)}")
    
    # Check if admin password is verified
    if not request.session.get('admin_password_verified', False):
        print("DEBUG: Admin password not verified, redirecting to admin_password_check")
        return redirect('store:admin_password_check')
    
    print("DEBUG: Accessing admin dashboard successfully")
    
    from .forms import CategoryForm
    category_form = CategoryForm()
    category_message = None
    if request.method == 'POST':
        action = request.POST.get('action')
        print("Action:", action)  # Debug print
        print("POST data:", request.POST)  # Debug print
        if action == 'add_product':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    product = form.save()
                    messages.success(request, f'Food "{product.name}" added successfully!')
                    return redirect('store:admin_dashboard')
                except Exception as e:
                    messages.error(request, f'Error saving food: {str(e)}')
            else:
                # Form is invalid, keep the form with errors to display them
                messages.error(request, 'Please correct the errors in the food form.')
                print("Form errors:", form.errors)  # Debug print
        elif action == 'edit_product':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                product = form.save()
                messages.success(request, f'Food "{product.name}" updated successfully!')
                return redirect('store:admin_dashboard')
            else:
                # Form is invalid, keep the form with errors to display them
                messages.error(request, 'Please correct the errors in the food form.')
        elif action == 'delete_product':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product_name = product.name
            product.delete()
            messages.success(request, f'Food "{product_name}" deleted successfully!')
            return redirect('store:admin_dashboard')
        elif action == 'add_category':
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category = category_form.save()
                messages.success(request, f'Category "{category.name}" added successfully!')
                return redirect('store:admin_dashboard')
            else:
                category_message = "Please correct the errors in the category form."
        elif action == 'delete_category':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category_name = category.name
            category.delete()
            messages.success(request, f'Category "{category_name}" and all its products have been deleted!')
            return redirect('store:admin_dashboard')
        else:
            form = ProductForm()
    else:
        form = ProductForm()
    
    # Get all products with search and filtering
    products = Product.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Filter by availability
    available_filter = request.GET.get('available', '')
    if available_filter == 'true':
        products = products.filter(available=True)
    elif available_filter == 'false':
        products = products.filter(available=False)
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    # Dashboard statistics
    total_products = Product.objects.count()
    available_products = Product.objects.filter(available=True).count()
    total_categories = Category.objects.count()
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='delivered').count()
    total_revenue = Order.objects.filter(paid=True).aggregate(total=Sum('items__price'))['total'] or 0
    
    # Payment statistics
    pending_payments = Order.objects.filter(payment_status='pending').count()
    completed_payments = Order.objects.filter(payment_status='completed').count()
    failed_payments = Order.objects.filter(payment_status='failed').count()
    
    # Recent products (last 5)
    recent_products = Product.objects.order_by('-created_at')[:5]
    
    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created')[:10]
    
    # Category breakdown
    category_stats = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:5]
    
    categories = Category.objects.all().order_by('name')
    context = {
        'form': form,
        'products': products,
        'search_query': search_query,
        'available_filter': available_filter,
        'total_products': total_products,
        'available_products': available_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'completed_payments': completed_payments,
        'failed_payments': failed_payments,
        'recent_products': recent_products,
        'recent_orders': recent_orders,
        'category_stats': category_stats,
        'admin_dashboard': True,
        'category_form': category_form,
        'category_message': category_message,
        'categories': categories,
    }
    
    return render(request, 'store/admin_dashboard.html', context)


@require_admin_password
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('store:admin_product_list')
    else:
        form = ProductForm()
    
    return render(request, 'store/admin/product_form.html', {
        'form': form,
        'title': 'Add New Product',
        'action': 'Create',
        'admin_dashboard': True,
    })


@require_admin_password
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('store:admin_product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'store/admin/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Edit Product',
        'action': 'Update',
        'admin_dashboard': True,
    })


@require_admin_password
def admin_product_list(request):
    products = Product.objects.all().order_by('-created_at')
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    # Filter by availability
    available_filter = request.GET.get('available', '')
    if available_filter == 'true':
        products = products.filter(available=True)
    elif available_filter == 'false':
        products = products.filter(available=False)
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    # Handle product creation form
    from .forms import ProductForm
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('store:admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'store/admin/product_list.html', {
        'products': products,
        'search_query': search_query,
        'available_filter': available_filter,
        'admin_dashboard': True,
        'form': form,
    })


@require_admin_password
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('store:admin_product_list')
    
    return render(request, 'store/admin/product_confirm_delete.html', {
        'product': product,
        'admin_dashboard': True,
    }) 