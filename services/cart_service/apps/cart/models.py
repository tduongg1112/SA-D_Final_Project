from decimal import Decimal

from django.db import models

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
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))

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
    product_id = models.PositiveBigIntegerField()
    product_slug = models.SlugField(max_length=180)
    product_name = models.CharField(max_length=180)
    category_name = models.CharField(max_length=120)
    brand = models.CharField(max_length=120)
    short_description = models.CharField(max_length=255)
    accent_color = models.CharField(max_length=7, default="#EEF4FF")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product_id")

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

# Create your models here.
