from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from apps.catalog.models import Product
from apps.ordering.models import Order
from apps.payments.models import PaymentRecord
from apps.shipping.models import Shipment
from config.service_clients import fetch_orders
from config.service_clients import fetch_payments
from config.service_clients import fetch_shipments


def humanize_status(value):
    if not value:
        return "Unavailable"
    return value.replace("_", " ").title()


@user_passes_test(lambda user: user.is_authenticated and user.is_staff)
def dashboard_home(request):
    remote_orders = fetch_orders()
    remote_payments = fetch_payments()
    remote_shipments = fetch_shipments()

    if remote_orders is not None and remote_payments is not None and remote_shipments is not None:
        recent_orders = remote_orders["items"][:5]
        for order in recent_orders:
            order["payment_status_label"] = humanize_status(order.get("payment_status"))
            order["shipping_status_label"] = humanize_status(order.get("shipping_status"))
        paid_orders = sum(1 for payment in remote_payments["items"] if payment["status"] == "paid")
        shipped_orders = sum(1 for shipment in remote_shipments["items"] if shipment["status"] != "pending")
    else:
        recent_orders = [
            {
                "id": order.id,
                "customer_name": order.customer_name,
                "total": str(order.total),
                "payment_status_label": order.payment.get_status_display(),
                "shipping_status_label": order.shipment.get_status_display(),
            }
            for order in Order.objects.select_related("payment", "shipment")[:5]
        ]
        paid_orders = PaymentRecord.objects.filter(status=PaymentRecord.Status.PAID).count()
        shipped_orders = Shipment.objects.exclude(status=Shipment.Status.PENDING).count()

    context = {
        "stats": {
            "products": Product.objects.count(),
            "orders": Order.objects.count(),
            "paid_orders": paid_orders,
            "shipped_orders": shipped_orders,
        },
        "recent_orders": recent_orders,
    }
    return render(request, "pages/dashboard/home.html", context)
