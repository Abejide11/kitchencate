from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Category, Product
from .forms import ProductForm, CategoryForm

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


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})


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
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
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
        'action': 'Create'
    })


@login_required
@user_passes_test(is_admin)
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
        'action': 'Update'
    })


@login_required
@user_passes_test(is_admin)
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
    
    return render(request, 'store/admin/product_list.html', {
        'products': products,
        'search_query': search_query,
        'available_filter': available_filter,
    })


@login_required
@user_passes_test(is_admin)
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('store:admin_product_list')
    
    return render(request, 'store/admin/product_confirm_delete.html', {
        'product': product
    }) 