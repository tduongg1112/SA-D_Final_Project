from django.db import models

from apps.ordering.models import Order


class Shipment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"

    order = models.OneToOneField(Order, related_name="shipment", on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    method = models.CharField(max_length=40, default="Standard delivery")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Shipment for order #{self.order_id}"

# Create your models here.
