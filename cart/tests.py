from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Product, Cart, CartItem, DiscountCode

class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Test Product', price=10.00, stock=50)
        self.discount_code = DiscountCode.objects.create(code='SAVE10', discount_percent=10)

    def test_add_to_cart_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        cart = Cart.objects.get(user=self.user, is_active=True)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.product.name, 'Test Product')

    def test_add_to_cart_guest_user(self):
        response = self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 3})
        session = self.client.session
        cart_items = session.get('cart_items', {})
        self.assertIn(str(self.product.id), cart_items)
        self.assertEqual(cart_items[str(self.product.id)]['quantity'], 3)

    def test_apply_discount_code(self):
        self.client.login(username='testuser', password='password')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        response = self.client.post('/cart/apply_discount/', {'code': 'SAVE10'})
        session = self.client.session
        self.assertEqual(session['discount'], 10)

    def test_clear_cart(self):
        self.client.login(username='testuser', password='password')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        response = self.client.get('/cart/clear_cart/')
        cart = Cart.objects.get(user=self.user, is_active=True)
        cart_items = CartItem.objects.filter(cart=cart)
        self.assertEqual(cart_items.count(), 0)

    def test_shipping_calculation(self):
        self.client.login(username='testuser', password='password')
        # Add items to exceed $100 after discount
        self.product.price = 60.00
        self.product.save()
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        response = self.client.get('/cart/')
        self.assertContains(response, 'Shipping: $0.0')

    def test_tax_calculation(self):
        self.client.login(username='testuser', password='password')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        response = self.client.get('/cart/')
        self.assertContains(response, 'Tax (10%): $1.0')

