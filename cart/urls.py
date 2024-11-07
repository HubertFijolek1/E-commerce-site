from django.urls import path
from . import views

urlpatterns = [
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    # Cart URLs
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('apply_discount/', views.apply_discount, name='apply_discount'),
    path('create_cart/', views.create_cart, name='create_cart'),
    path('select_cart/<int:cart_id>/', views.select_cart, name='select_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('', views.cart_detail, name='cart_detail'),
]
