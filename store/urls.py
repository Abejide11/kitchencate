from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<str:slug>/', views.category_detail, name='category_detail'),
    
    # Admin URLs
    path('admin-password/', views.admin_password_check, name='admin_password_check'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/products/', views.admin_product_list, name='admin_product_list'),
    path('manage/products/create/', views.admin_product_create, name='admin_product_create'),
    path('manage/products/<int:pk>/edit/', views.admin_product_update, name='admin_product_update'),
    path('manage/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
] 