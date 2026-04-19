from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.ordering.forms import CheckoutForm
from config.service_clients import add_cart_item
from config.service_clients import fetch_cart
from config.service_clients import remove_cart_item
from config.service_clients import update_cart_item


def empty_cart():
    return {
        "session_key": "",
        "item_count": 0,
        "subtotal": "0.00",
        "shipping_fee": "0.00",
        "total": "0.00",
        "items": [],
    }


def cart_detail(request):
    cart = fetch_cart(request) or empty_cart()
    return render(
        request,
        "pages/cart/detail.html",
        {"cart": cart, "checkout_form": CheckoutForm()},
    )


@require_POST
def add_to_cart(request, product_id):
    if add_cart_item(request, product_id, 1) is None:
        messages.error(request, "Cart service is currently unavailable.")
    return redirect("cart:detail")


@require_POST
def update_item(request, item_id):
    quantity = max(int(request.POST.get("quantity", 1)), 1)
    if update_cart_item(request, item_id, quantity) is None:
        messages.error(request, "Cart service is currently unavailable.")
    return redirect("cart:detail")


@require_POST
def remove_item(request, item_id):
    if remove_cart_item(request, item_id) is None:
        messages.error(request, "Cart service is currently unavailable.")
    return redirect("cart:detail")


def cart_api(request):
    payload = fetch_cart(request) or empty_cart()
    return JsonResponse(payload)
