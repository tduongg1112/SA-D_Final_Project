from decimal import Decimal

from django.db import models

from apps.catalog.models import Product


class Cart(models.Model):
    session_key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Cart {self.session_key}"

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.select_related("product")), Decimal("0.00"))

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def shipping_fee(self):
        return Decimal("5.00") if self.item_count else Decimal("0.00")

    @property
    def total(self):
        return self.subtotal + self.shipping_fee


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.product.price * self.quantity

# Create your models here.
