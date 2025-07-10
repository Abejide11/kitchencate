from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<str:slug>/', views.category_detail, name='category_detail'),
    
    # Admin URLs
    path('admin/products/', views.admin_product_list, name='admin_product_list'),
    path('admin/products/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/products/<int:pk>/edit/', views.admin_product_update, name='admin_product_update'),
    path('admin/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
] 