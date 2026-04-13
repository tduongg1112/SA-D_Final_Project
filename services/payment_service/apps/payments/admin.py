from django.contrib import admin

from apps.payments.models import PaymentRecord


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("order_id", "provider", "amount", "status", "transaction_reference", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("transaction_reference", "=order_id")
