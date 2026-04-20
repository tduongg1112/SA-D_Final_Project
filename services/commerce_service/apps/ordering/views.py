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


DEFAULT_CHECKOUT_PROFILE = {
    "customer_name": "NovaMarket Demo",
    "customer_email": "demo@novamarket.local",
    "customer_phone": "0000 000 000",
    "shipping_address": "Demo checkout profile applied automatically from the storefront shell.",
    "note": "Quick checkout from the storefront demo.",
}


def humanize_status(value):
    if not value:
        return "Unavailable"
    return value.replace("_", " ").title()


def get_checkout_context(request):
    cart = fetch_cart(request)
    if cart is None:
        return None, None
    return cart["items"], cart


def default_checkout_profile(request):
    profile = DEFAULT_CHECKOUT_PROFILE.copy()
    if request.user.is_authenticated:
        display_name = request.user.get_full_name().strip() or request.user.get_username()
        profile["customer_name"] = display_name or profile["customer_name"]
        if request.user.email:
            profile["customer_email"] = request.user.email
    return profile


def build_checkout_payload(request, form, items):
    profile = default_checkout_profile(request)
    for field in ("customer_name", "customer_email", "customer_phone", "shipping_address", "note"):
        value = (form.cleaned_data.get(field) or "").strip()
        if value:
            profile[field] = value

    return {
        "customer_name": profile["customer_name"],
        "customer_email": profile["customer_email"],
        "customer_phone": profile["customer_phone"],
        "shipping_address": profile["shipping_address"],
        "note": profile["note"],
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
    form.is_valid()

    order = create_order(build_checkout_payload(request, form, items))
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
