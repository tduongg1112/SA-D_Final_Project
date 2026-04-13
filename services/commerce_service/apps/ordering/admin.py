from django.contrib import admin

from apps.ordering.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_email", "total", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("customer_name", "customer_email", "customer_phone")
    inlines = [OrderItemInline]

# Register your models here.
