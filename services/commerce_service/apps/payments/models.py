from django.db import models

from apps.ordering.models import Order


class PaymentRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, default="MockPay")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_reference = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_reference} - {self.status}"

# Create your models here.
