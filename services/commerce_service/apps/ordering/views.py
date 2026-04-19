from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.ordering.forms import CheckoutForm
from config.service_clients import clear_cart
from config.service_clients import create_order
from config.service_clients import fetch_cart
from config.service_clients import fetch_order_detail
from config.service_clients import fetch_orders

def humanize_status(value):
    if not value:
        return "Unavailable"
    return value.replace("_", " ").title()

def get_checkout_context(request):
    cart = fetch_cart(request)
    if cart is None:
        return None, None
    return cart["items"], cart


def build_checkout_payload(form, items):
    return {
        "customer_name": form.cleaned_data["customer_name"],
        "customer_email": form.cleaned_data["customer_email"],
        "customer_phone": form.cleaned_data["customer_phone"],
        "shipping_address": form.cleaned_data["shipping_address"],
        "note": form.cleaned_data["note"],
        "items": [
            {
                "product_id": item["product_id"],
                "product_name": item["product"],
                "unit_price": item["price"],
                "quantity": item["quantity"],
                "line_total": item["line_total"],
            }
            for item in items
        ],
    }


@require_POST
def checkout(request):
    items, cart = get_checkout_context(request)
    if not items:
        return redirect("cart:detail")

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "pages/cart/detail.html",
            {"cart": cart, "checkout_form": form},
            status=400,
        )

    order = create_order(build_checkout_payload(form, items))
    if order is None:
        form.add_error(None, "The ordering service is currently unavailable.")
        return render(
            request,
            "pages/cart/detail.html",
            {"cart": cart, "checkout_form": form},
            status=502,
        )

    if clear_cart(request) is None:
        messages.warning(request, "The cart could not be cleared automatically after checkout.")

    return redirect("ordering:success", order_id=order["id"])


def order_success(request, order_id):
    order = fetch_order_detail(order_id)
    if order is None:
        return render(request, "pages/orders/success.html", {"order": None}, status=502)
    order["payment_status_label"] = humanize_status(order.get("payment_status"))
    order["shipping_status_label"] = humanize_status(order.get("shipping_status"))
    return render(request, "pages/orders/success.html", {"order": order})


def orders_api(request):
    payload = fetch_orders()
    if payload is None:
        return JsonResponse({"detail": "Ordering service is unavailable."}, status=502)
    return JsonResponse(payload)
