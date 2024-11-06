from django.shortcuts import redirect, get_object_or_404
from .models import Product, CartItem

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    # Validate stock
    if quantity > product.stock:
        # Handle out-of-stock scenario
        pass
    else:
        cart_item = CartItem.objects.create(product=product, quantity=quantity)
        # Save to session or user cart
    return redirect('cart_detail')

