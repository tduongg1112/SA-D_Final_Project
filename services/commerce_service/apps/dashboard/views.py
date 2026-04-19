from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from config.service_clients import fetch_orders
from config.service_clients import fetch_payments
from config.service_clients import fetch_products
from config.service_clients import fetch_shipments


def humanize_status(value):
    if not value:
        return "Unavailable"
    return value.replace("_", " ").title()


@user_passes_test(lambda user: user.is_authenticated and user.is_staff)
def dashboard_home(request):
    remote_products = fetch_products()
    remote_orders = fetch_orders()
    remote_payments = fetch_payments()
    remote_shipments = fetch_shipments()

    if (
        remote_products is not None
        and remote_orders is not None
        and remote_payments is not None
        and remote_shipments is not None
    ):
        recent_orders = remote_orders["items"][:5]
        for order in recent_orders:
            order["payment_status_label"] = humanize_status(order.get("payment_status"))
            order["shipping_status_label"] = humanize_status(order.get("shipping_status"))
        paid_orders = sum(1 for payment in remote_payments["items"] if payment["status"] == "paid")
        shipped_orders = sum(1 for shipment in remote_shipments["items"] if shipment["status"] != "pending")
        product_count = len(remote_products["items"])
        order_count = len(remote_orders["items"])
    else:
        recent_orders = []
        paid_orders = 0
        shipped_orders = 0
        product_count = 0
        order_count = 0

    context = {
        "stats": {
            "products": product_count,
            "orders": order_count,
            "paid_orders": paid_orders,
            "shipped_orders": shipped_orders,
        },
        "recent_orders": recent_orders,
    }
    return render(request, "pages/dashboard/home.html", context)
