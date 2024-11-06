from django.shortcuts import redirect, get_object_or_404, render
from .models import Product, CartItem, DiscountCode
from django.contrib import messages

# Constants for tax and shipping
TAX_RATE = 0.10  # 10% tax
SHIPPING_COST = 5.00  # Flat shipping rate

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart_items = request.session.get('cart_items', {})
    current_quantity = cart_items.get(str(product_id), {}).get('quantity', 0)
    total_quantity = current_quantity + quantity

    # Validate stock
    if total_quantity > product.stock:
        messages.error(request, "Not enough stock available.")
        return redirect('product_detail', product_id=product_id)

    cart_items[str(product_id)] = {'quantity': total_quantity, 'price': str(product.price)}
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

    discount_percent = request.session.get('discount', 0)
    discount_amount = total_price * (discount_percent / 100)
    price_after_discount = total_price - discount_amount

    tax_amount = price_after_discount * TAX_RATE
    final_total = price_after_discount + tax_amount + SHIPPING_COST

    context = {
        'cart_products': cart_products,
        'total_price': total_price,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'price_after_discount': price_after_discount,
        'tax_amount': tax_amount,
        'shipping_cost': SHIPPING_COST,
        'final_total': final_total,
    }
    return render(request, 'cart/cart_detail.html', context)


def remove_from_cart(request, product_id):
    cart_items = request.session.get('cart_items', {})
    if str(product_id) in cart_items:
        del cart_items[str(product_id)]
        request.session['cart_items'] = cart_items
        messages.success(request, "Item removed from cart.")
    return redirect('cart_detail')


def update_cart(request, product_id):
    cart_items = request.session.get('cart_items', {})
    quantity = int(request.POST.get('quantity', 1))

    # Validate stock
    product = get_object_or_404(Product, id=product_id)
    if quantity > product.stock:
        messages.error(request, "Not enough stock available.")
        return redirect('cart_detail')

    cart_items[str(product_id)]['quantity'] = quantity
    request.session['cart_items'] = cart_items
    messages.success(request, "Cart updated.")
    return redirect('cart_detail')


def apply_discount(request):
    code = request.POST.get('code')
    try:
        discount = DiscountCode.objects.get(code=code)
        request.session['discount'] = discount.discount_percent
        messages.success(request, "Discount code applied.")
    except DiscountCode.DoesNotExist:
        messages.error(request, "Invalid discount code.")
    return redirect('cart_detail')


def checkout(request):
    # Calculate total price including taxes and shipping
    return render(request, 'cart/checkout.html', context)
