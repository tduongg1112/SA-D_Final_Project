from django.contrib import admin

from apps.payments.models import PaymentRecord


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("transaction_reference", "order", "provider", "status", "created_at")
    list_filter = ("status", "provider")

# Register your models here.
