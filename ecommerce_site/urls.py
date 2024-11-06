from django.contrib import admin
from django.urls import path, include
from cart import views as cart_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', cart_views.product_list, name='home'),
]
