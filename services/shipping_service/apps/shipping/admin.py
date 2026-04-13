from django.contrib import admin

from apps.shipping.models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order_id", "recipient_name", "method", "status", "tracking_code", "created_at")
    list_filter = ("status", "method")
    search_fields = ("=order_id", "tracking_code", "recipient_name")
