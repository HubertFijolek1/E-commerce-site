from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    """
    Model representing a product in the store.
    """
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Cart(models.Model):
    """
    Model representing a shopping cart associated with a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart ({self.user.username})"

class CartItem(models.Model):
    """
    Model representing an item in a shopping cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class DiscountCode(models.Model):
    """
    Model representing a discount code.
    """
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.FloatField()

    def __str__(self):
        return self.code



