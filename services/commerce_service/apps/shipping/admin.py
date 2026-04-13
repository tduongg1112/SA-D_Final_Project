from django.contrib import admin

from apps.shipping.models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "recipient_name", "method", "status", "created_at")
    list_filter = ("status", "method")

# Register your models here.
