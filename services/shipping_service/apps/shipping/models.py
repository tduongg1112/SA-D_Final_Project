from django.db import models


class Shipment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"

    order_id = models.PositiveBigIntegerField(unique=True)
    recipient_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    method = models.CharField(max_length=40, default="Standard delivery")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    tracking_code = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Shipment {self.tracking_code}"
