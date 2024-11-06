from django.shortcuts import redirect, get_object_or_404, render
from .models import Product, CartItem
from django.contrib import messages


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Validate stock
    if quantity > product.stock:
        messages.error(request, "Not enough stock available.")
        return redirect('product_detail', product_id=product_id)

    cart_items = request.session.get('cart_items', {})

    if str(product_id) in cart_items:
        cart_items[str(product_id)]['quantity'] += quantity
    else:
        cart_items[str(product_id)] = {'quantity': quantity, 'price': str(product.price)}

    request.session['cart_items'] = cart_items
    messages.success(request, "Product added to cart.")
    return redirect('cart_detail')

def cart_detail(request):
    cart_items = request.session.get('cart_items', {})
    products = Product.objects.filter(id__in=cart_items.keys())
    cart_products = []
    total_price = 0

    for product in products:
        quantity = cart_items[str(product.id)]['quantity']
        subtotal = product.price * quantity
        total_price += subtotal
        cart_products.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    context = {
        'cart_products': cart_products,
        'total_price': total_price,
    }
    return render(request, 'cart/cart_detail.html', context)


def remove_from_cart(request, item_id):
    # Remove item and update total price
    return redirect('cart_detail')

def update_cart(request, item_id):
    quantity = int(request.POST.get('quantity'))
    # Update item quantity and reflect changes in price
    return redirect('cart_detail')

def apply_discount(request):
    code = request.POST.get('code')
    # Validate and apply discount
    return redirect('checkout')

def checkout(request):
    # Calculate total price including taxes and shipping
    return render(request, 'cart/checkout.html', context)
