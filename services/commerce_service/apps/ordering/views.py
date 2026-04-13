import os
from decimal import Decimal
from uuid import uuid4

import httpx
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.cart.models import CartItem
from apps.cart.utils import serialize_cart
from apps.catalog.models import Product
from apps.ordering.forms import CheckoutForm
from apps.ordering.models import Order, OrderItem
from apps.payments.models import PaymentRecord
from apps.shipping.models import Shipment
from config.service_clients import clear_cart
from config.service_clients import fetch_cart
from config.service_clients import fetch_order_detail
from config.service_clients import fetch_orders

SHIPPING_FEE = Decimal("5.00")
ORDERING_SERVICE_URL = os.getenv("ORDERING_SERVICE_URL", "").rstrip("/")


def humanize_status(value):
    if not value:
        return "Unavailable"
    return value.replace("_", " ").title()


def serialize_local_order(order):
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "shipping_address": order.shipping_address,
        "subtotal": str(order.subtotal),
        "shipping_fee": str(order.shipping_fee),
        "total": str(order.total),
        "status": order.status,
        "payment_status": order.payment.status,
        "payment_reference": order.payment.transaction_reference,
        "payment_status_label": order.payment.get_status_display(),
        "shipping_status": order.shipment.status,
        "shipping_status_label": order.shipment.get_status_display(),
        "tracking_code": f"LOCAL-{order.id}",
        "items": [
            {
                "product_name": item.product_name,
                "unit_price": str(item.unit_price),
                "quantity": item.quantity,
                "line_total": str(item.line_total),
            }
            for item in order.items.all()
        ],
    }


def normalize_checkout_items(items):
    normalized_items = []
    for item in items:
        if isinstance(item, dict):
            normalized_items.append(
                {
                    "product_id": item["product_id"],
                    "product_name": item["product"],
                    "unit_price": Decimal(str(item["price"])),
                    "quantity": int(item["quantity"]),
                    "line_total": Decimal(str(item["line_total"])),
                }
            )
        else:
            normalized_items.append(
                {
                    "product_id": item.product_id,
                    "product_name": item.product.name,
                    "unit_price": item.product.price,
                    "quantity": item.quantity,
                    "line_total": item.line_total,
                }
            )
    return normalized_items


def get_checkout_context(request):
    remote_cart = fetch_cart(request)
    if remote_cart is not None:
        return remote_cart["items"], remote_cart, None

    local_cart = request.cart if hasattr(request, "cart") else None
    if local_cart is None:
        from apps.cart.utils import get_or_create_cart

        local_cart = get_or_create_cart(request)
    items = list(local_cart.items.select_related("product"))
    return items, serialize_cart(local_cart), local_cart


def create_order_locally(form, items):
    normalized_items = normalize_checkout_items(items)
    subtotal = sum((item["line_total"] for item in normalized_items), Decimal("0.00"))
    total = subtotal + SHIPPING_FEE
    order = Order.objects.create(
        customer_name=form.cleaned_data["customer_name"],
        customer_email=form.cleaned_data["customer_email"],
        customer_phone=form.cleaned_data["customer_phone"],
        shipping_address=form.cleaned_data["shipping_address"],
        note=form.cleaned_data["note"],
        subtotal=subtotal,
        shipping_fee=SHIPPING_FEE,
        total=total,
        status=Order.Status.CONFIRMED,
    )
    for item in normalized_items:
        OrderItem.objects.create(
            order=order,
            product_name=item["product_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            line_total=item["line_total"],
        )
    PaymentRecord.objects.create(
        order=order,
        status=PaymentRecord.Status.PAID,
        transaction_reference=f"MOCK-{uuid4().hex[:10].upper()}",
    )
    Shipment.objects.create(
        order=order,
        recipient_name=order.customer_name,
        phone=order.customer_phone,
        address=order.shipping_address,
        status=Shipment.Status.PREPARING,
    )
    return order


def create_order_via_service(form, items):
    normalized_items = normalize_checkout_items(items)
    payload = {
        "customer_name": form.cleaned_data["customer_name"],
        "customer_email": form.cleaned_data["customer_email"],
        "customer_phone": form.cleaned_data["customer_phone"],
        "shipping_address": form.cleaned_data["shipping_address"],
        "note": form.cleaned_data["note"],
        "items": [
            {
                "product_name": item["product_name"],
                "unit_price": str(item["unit_price"]),
                "quantity": item["quantity"],
                "line_total": str(item["line_total"]),
            }
            for item in normalized_items
        ],
    }
    with httpx.Client(timeout=20.0) as client:
        response = client.post(f"{ORDERING_SERVICE_URL}/api/orders/checkout/", json=payload)
    if response.status_code != 201:
        raise RuntimeError(f"Ordering service checkout failed: {response.text}")
    return response.json()["id"]


@require_POST
def checkout(request):
    items, cart, local_cart = get_checkout_context(request)
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

    try:
        if ORDERING_SERVICE_URL:
            order_id = create_order_via_service(form, items)
        else:
            order = create_order_locally(form, items)
            order_id = order.id
    except Exception:
        form.add_error(None, "The ordering service is currently unavailable.")
        return render(
            request,
            "pages/cart/detail.html",
            {"cart": cart, "checkout_form": form},
            status=502,
        )

    for item in normalize_checkout_items(items):
        product = Product.objects.get(pk=item["product_id"])
        product.stock_quantity = max(product.stock_quantity - item["quantity"], 0)
        product.save(update_fields=["stock_quantity"])

    if clear_cart(request) is None and local_cart is not None:
        CartItem.objects.filter(cart=local_cart).delete()

    return redirect("ordering:success", order_id=order_id)


def order_success(request, order_id):
    if ORDERING_SERVICE_URL:
        try:
            order = fetch_order_detail(order_id)
        except httpx.HTTPError:
            order = None
    else:
        order = None

    if order is None:
        order = get_object_or_404(
            Order.objects.prefetch_related("items").select_related("payment", "shipment"),
            pk=order_id,
        )
        order = serialize_local_order(order)
    else:
        order["payment_status_label"] = humanize_status(order.get("payment_status"))
        order["shipping_status_label"] = humanize_status(order.get("shipping_status"))
    return render(request, "pages/orders/success.html", {"order": order})


def orders_api(request):
    if ORDERING_SERVICE_URL:
        try:
            return JsonResponse(fetch_orders())
        except httpx.HTTPError:
            pass

    orders = Order.objects.prefetch_related("items").select_related("payment", "shipment")[:20]
    return JsonResponse(
        {
            "items": [
                {
                    "id": order.id,
                    "customer_name": order.customer_name,
                    "total": str(order.total),
                    "status": order.status,
                    "payment_status": order.payment.status,
                    "shipping_status": order.shipment.status,
                }
                for order in orders
            ]
        }
    )
