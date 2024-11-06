from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('apply_discount/', views.apply_discount, name='apply_discount'),
    path('create_cart/', views.create_cart, name='create_cart'),
    path('select_cart/<int:cart_id>/', views.select_cart, name='select_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('', views.cart_detail, name='cart_detail'),
]