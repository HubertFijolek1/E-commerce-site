from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, DiscountCode, Cart, CartItem
from django.contrib.auth.decorators import login_required

# Constants for tax and shipping
TAX_RATE = 0.10  # 10% tax
SHIPPING_COST = 5.00  # Flat shipping rate

def add_to_cart(request, product_id):
    """
    View to add a product to the cart with quantity selection.
    """
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Validate stock
    if quantity > product.stock:
        messages.error(request, "Not enough stock available.")
        return redirect('product_detail', product_id=product_id)

    if request.user.is_authenticated:
        # Get the active cart for the user
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart:
            messages.error(request, "No active cart found. Please select or create a cart.")
            return redirect('cart_detail')
        # Check if the cart item already exists
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        total_quantity = cart_item.quantity + quantity
        if total_quantity > product.stock:
            messages.error(request, "Not enough stock available.")
            return redirect('product_detail', product_id=product_id)
        cart_item.quantity = total_quantity
        cart_item.save()
    else:
        # Session-based cart for guest users
        cart_items = request.session.get('cart_items', {})
        current_quantity = cart_items.get(str(product_id), {}).get('quantity', 0)
        total_quantity = current_quantity + quantity
        if total_quantity > product.stock:
            messages.error(request, "Not enough stock available.")
            return redirect('product_detail', product_id=product_id)
        cart_items[str(product_id)] = {'quantity': total_quantity, 'price': str(product.price)}
        request.session['cart_items'] = cart_items

    messages.success(request, "Product added to cart.")
    return redirect('cart_detail')

def cart_detail(request):
    """
    View to display items in the cart and the total price.
    """
    cart_products = []
    total_price = 0

    if request.user.is_authenticated:
        # Retrieve all carts for the user
        carts = Cart.objects.filter(user=request.user)
        # Retrieve items from the active cart
        cart = carts.filter(is_active=True).first()
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)
            for item in cart_items:
                subtotal = item.product.price * item.quantity
                total_price += subtotal
                cart_products.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'subtotal': subtotal
                })
        else:
            cart_items = []
            messages.error(request, "No active cart found. Please select or create a cart.")
    else:
        carts = None
        # Retrieve cart items from session for guest users
        cart_items = request.session.get('cart_items', {})
        products = Product.objects.filter(id__in=cart_items.keys())
        for product in products:
            quantity = cart_items[str(product.id)]['quantity']
            subtotal = product.price * quantity
            total_price += subtotal
            cart_products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

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
        'carts': carts,
    }
    return render(request, 'cart/cart_detail.html', context)

def remove_from_cart(request, product_id):
    """
    View to remove a product from the cart.
    """
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    else:
        cart_items = request.session.get('cart_items', {})
        if str(product_id) in cart_items:
            del cart_items[str(product_id)]
            request.session['cart_items'] = cart_items

    messages.success(request, "Item removed from cart.")
    return redirect('cart_detail')

def update_cart(request, product_id):
    """
    View to update the quantity of a product in the cart.
    """
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id)

    # Validate stock
    if quantity > product.stock:
        messages.error(request, "Not enough stock available.")
        return redirect('cart_detail')

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                cart_item.quantity = quantity
                cart_item.save()
    else:
        cart_items = request.session.get('cart_items', {})
        if str(product_id) in cart_items:
            cart_items[str(product_id)]['quantity'] = quantity
            request.session['cart_items'] = cart_items

    messages.success(request, "Cart updated.")
    return redirect('cart_detail')

def apply_discount(request):
    """
    View to apply a discount code during checkout.
    """
    code = request.POST.get('code')
    try:
        discount = DiscountCode.objects.get(code=code)
        request.session['discount'] = discount.discount_percent
        messages.success(request, "Discount code applied.")
    except DiscountCode.DoesNotExist:
        messages.error(request, "Invalid discount code.")
    return redirect('cart_detail')

@login_required
def create_cart(request):
    """
    View to allow users to create a new cart.
    """
    if request.method == 'POST':
        name = request.POST.get('name', 'New Cart')
        # Deactivate all other carts
        Cart.objects.filter(user=request.user).update(is_active=False)
        cart = Cart.objects.create(user=request.user, name=name, is_active=True)
        messages.success(request, f"Cart '{name}' created and set as active.")
        return redirect('cart_detail')
    return render(request, 'cart/create_cart.html')

@login_required
def select_cart(request, cart_id):
    """
    View to allow users to select an existing cart as active.
    """
    # Deactivate all other carts
    Cart.objects.filter(user=request.user).update(is_active=False)
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart.is_active = True
    cart.save()
    messages.success(request, f"Cart '{cart.name}' is now active.")
    return redirect('cart_detail')

def clear_cart(request):
    """
    View to clear all items from the cart.
    """
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            # Delete all items in the active cart
            CartItem.objects.filter(cart=cart).delete()
            messages.success(request, "Your cart has been cleared.")
        else:
            messages.error(request, "No active cart found to clear.")
    else:
        # Clear session-based cart for guest users
        request.session['cart_items'] = {}
        messages.success(request, "Your cart has been cleared.")
    return redirect('cart_detail')
