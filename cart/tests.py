from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Product, Cart, CartItem, DiscountCode

class ProductViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create sample products
        self.product1 = Product.objects.create(name='Product 1', price=Decimal('19.99'), stock=100)
        self.product2 = Product.objects.create(name='Product 2', price=Decimal('29.99'), stock=50)

    def test_product_list_view(self):
        response = self.client.get('/cart/products/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product 1')
        self.assertContains(response, 'Product 2')

    def test_product_detail_view(self):
        response = self.client.get(f'/cart/products/{self.product1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product 1')
        self.assertContains(response, '19.99')
        self.assertContains(response, '100')


class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user and log them in
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # Create sample product and discount code
        self.product = Product.objects.create(name='Test Product', price=Decimal('10.00'), stock=50)
        self.discount_code = DiscountCode.objects.create(code='SAVE10', discount_percent=10)

        # Create an active cart for the user by default
        self.cart = Cart.objects.create(user=self.user, is_active=True)

    def test_add_to_cart_authenticated_user(self):
        response = self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        cart_item = CartItem.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.product.name, 'Test Product')
        self.assertEqual(response.status_code, 302)  # Should redirect to cart detail

    def test_apply_discount_code(self):
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        self.client.post('/cart/apply_discount/', {'code': 'SAVE10'})

        # Check that the discount was applied correctly
        response = self.client.get('/cart/')
        self.assertContains(response, 'Discount (10.00%)')  # Updated to match rendered output
        self.assertContains(response, '-$2.00')  # 10% of 20.00 is 2.00

    def test_tax_calculation_in_cart(self):
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tax (10%)')
        self.assertContains(response, '$1.00')  # 10% of 10.00 is 1.00

    def test_free_shipping_threshold(self):
        # Set product price to test free shipping threshold
        self.product.price = Decimal('60.00')
        self.product.save()
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})

        response = self.client.get('/cart/')
        self.assertContains(response, 'Shipping: $0.00')  # Free shipping for orders over $100

    def test_flat_shipping_rate_below_threshold(self):
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        response = self.client.get('/cart/')
        self.assertContains(response, 'Shipping: $10.00')  # Flat rate for orders below $100

    def test_clear_cart(self):
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        response = self.client.get('/cart/clear_cart/')

        # Ensure cart is cleared
        cart_items = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(cart_items.count(), 0)
        self.assertEqual(response.status_code, 302)

    def test_select_cart(self):
        # Create additional carts for testing selection
        cart1 = Cart.objects.create(user=self.user, name="Cart 1", is_active=False)
        cart2 = Cart.objects.create(user=self.user, name="Cart 2", is_active=True)

        # Select cart1 to activate it
        response = self.client.get(f'/cart/select_cart/{cart1.id}/')
        cart1.refresh_from_db()
        cart2.refresh_from_db()

        self.assertTrue(cart1.is_active)
        self.assertFalse(cart2.is_active)
