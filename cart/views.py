from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, DiscountCode, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.urls import reverse


# Constants for tax and shipping
TAX_RATE = Decimal('0.10')  # 10% tax as Decimal
FREE_SHIPPING_THRESHOLD = Decimal('100.00')
FLAT_SHIPPING_RATE = Decimal('10.00')

def add_to_cart(request, product_id):
    """
    View to add a product to the cart with quantity selection.
    """
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity.")
        return redirect('product_detail', product_id=product_id)

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

        # Get or create CartItem with initial quantity=0
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0}
        )

        # Calculate new total quantity
        total_quantity = cart_item.quantity + quantity
        if total_quantity > product.stock:
            messages.error(request, "Not enough stock available.")
            return redirect('product_detail', product_id=product_id)

        # Update the quantity
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
    return redirect(reverse('cart_detail'))


def cart_detail(request):
    """
    View to display items in the cart and the total price, including shipping calculation.
    """
    cart_products = []
    total_price = Decimal('0.00')

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

    discount_percent = Decimal(request.session.get('discount', 0))
    discount_amount = total_price * (discount_percent / Decimal('100'))
    price_after_discount = total_price - discount_amount

    tax_amount = price_after_discount * TAX_RATE

    # Dynamic shipping cost based on total price after discount
    if price_after_discount >= FREE_SHIPPING_THRESHOLD:
        shipping_cost = Decimal('0.00')  # Free shipping
    else:
        shipping_cost = FLAT_SHIPPING_RATE  # Flat rate shipping

    final_total = price_after_discount + tax_amount + shipping_cost

    context = {
        'cart_products': cart_products,
        'total_price': total_price,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'price_after_discount': price_after_discount,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
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
        if discount.is_valid():
            request.session['discount'] = str(discount.discount_percent)
            request.session['discount_code'] = discount.code
            messages.success(request, "Discount code applied.")
        else:
            messages.error(request, "Discount code is invalid or expired.")
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

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    if not cart:
        messages.error(request, "No active cart to checkout.")
        return redirect('cart_detail')

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_detail')

    # Calculate totals
    total_price = Decimal('0.00')
    for item in cart_items:
        total_price += item.product.price * item.quantity

    discount_percent = Decimal(request.session.get('discount', '0'))
    discount_amount = total_price * (discount_percent / Decimal('100'))
    price_after_discount = total_price - discount_amount

    tax_amount = price_after_discount * TAX_RATE

    if price_after_discount >= FREE_SHIPPING_THRESHOLD:
        shipping_cost = Decimal('0.00')
    else:
        shipping_cost = FLAT_SHIPPING_RATE

    final_total = price_after_discount + tax_amount + shipping_cost

    # Create Order
    order = Order.objects.create(
        user=request.user,
        total_amount=total_price,
        discount_code=DiscountCode.objects.filter(code=request.session.get('discount_code')).first(),
        tax_amount=tax_amount,
        shipping_cost=shipping_cost,
        final_total=final_total
    )
    if order.discount_code:
        order.discount_code.times_used += 1
        order.discount_code.save()

    # Create OrderItems and deduct stock
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_purchase=item.product.price
        )
        # Deduct stock
        item.product.stock -= item.quantity
        item.product.save()

    # Clear cart
    cart_items.delete()
    cart.is_active = False
    cart.save()
    request.session.pop('discount', None)
    request.session.pop('discount_code', None)

    messages.success(request, "Purchase successful! Your order has been placed.")
    return redirect('home')


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

def product_list(request):
    """
    View to display a list of all products.
    """
    products = Product.objects.all()
    return render(request, 'cart/product_list.html', {'products': products})

def product_detail(request, product_id):
    """
    View to display the details of a single product.
    """
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'cart/product_detail.html', {'product': product})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cart/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'cart/order_detail.html', {'order': order})