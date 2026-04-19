import json
import os
from decimal import Decimal

import httpx
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.ordering.models import Order
from apps.ordering.models import OrderItem

SHIPPING_FEE = Decimal("5.00")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "").rstrip("/")
SHIPPING_SERVICE_URL = os.getenv("SHIPPING_SERVICE_URL", "").rstrip("/")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "").rstrip("/")


def create_payment_record(order):
    if not PAYMENT_SERVICE_URL:
        return None

    try:
        response = httpx.post(
            f"{PAYMENT_SERVICE_URL}/api/payments/",
            json={
                "order_id": order.id,
                "amount": str(order.total),
                "provider": "MockPay",
                "status": "paid",
            },
            timeout=5.0,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json()


def create_shipment_record(order):
    if not SHIPPING_SERVICE_URL:
        return None

    try:
        response = httpx.post(
            f"{SHIPPING_SERVICE_URL}/api/shipping/",
            json={
                "order_id": order.id,
                "recipient_name": order.customer_name,
                "phone": order.customer_phone,
                "address": order.shipping_address,
                "method": "Standard delivery",
                "status": "preparing",
            },
            timeout=5.0,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json()


def reserve_stock(items):
    if not PRODUCT_SERVICE_URL:
        return None

    payload = {
        "items": [
            {
                "product_id": int(item["product_id"]),
                "quantity": int(item["quantity"]),
            }
            for item in items
        ]
    }

    response = httpx.post(
        f"{PRODUCT_SERVICE_URL}/api/products/stock/reserve/",
        json=payload,
        timeout=5.0,
    )
    if response.status_code == 409:
        raise ValueError(response.json().get("detail", "Insufficient stock."))
    response.raise_for_status()
    return response.json()


def fetch_payment_record(order_id):
    if not PAYMENT_SERVICE_URL:
        return None

    try:
        response = httpx.get(f"{PAYMENT_SERVICE_URL}/api/payments/order/{order_id}/", timeout=3.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json()


def fetch_shipment_record(order_id):
    if not SHIPPING_SERVICE_URL:
        return None

    try:
        response = httpx.get(f"{SHIPPING_SERVICE_URL}/api/shipping/order/{order_id}/", timeout=3.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json()


@csrf_exempt
def checkout_api(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    items = payload.get("items", [])
    required_fields = ["customer_name", "customer_email", "customer_phone", "shipping_address"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing or not items:
        return JsonResponse(
            {"detail": "Missing required checkout fields or cart items.", "missing": missing},
            status=400,
        )

    if PRODUCT_SERVICE_URL:
        missing_product_ids = [index for index, item in enumerate(items) if not item.get("product_id")]
        if missing_product_ids:
            return JsonResponse(
                {"detail": "Each checkout item must include product_id.", "indexes": missing_product_ids},
                status=400,
            )

    try:
        reserve_stock(items)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=409)
    except httpx.HTTPError:
        return JsonResponse({"detail": "Product service is unavailable."}, status=502)

    subtotal = sum((Decimal(str(item["line_total"])) for item in items), Decimal("0.00"))
    total = subtotal + SHIPPING_FEE
    order = Order.objects.create(
        customer_name=payload["customer_name"],
        customer_email=payload["customer_email"],
        customer_phone=payload["customer_phone"],
        shipping_address=payload["shipping_address"],
        note=payload.get("note", ""),
        subtotal=subtotal,
        shipping_fee=SHIPPING_FEE,
        total=total,
        status=Order.Status.CONFIRMED,
    )
    for item in items:
        OrderItem.objects.create(
            order=order,
            product_id=item.get("product_id"),
            product_name=item["product_name"],
            unit_price=Decimal(str(item["unit_price"])),
            quantity=int(item["quantity"]),
            line_total=Decimal(str(item["line_total"])),
        )
    payment = create_payment_record(order)
    shipment = create_shipment_record(order)
    return JsonResponse(
        {
            "id": order.id,
            "status": order.status,
            "payment_status": payment["status"] if payment else None,
            "shipping_status": shipment["status"] if shipment else None,
        },
        status=201,
    )


def orders_api(request):
    orders = Order.objects.prefetch_related("items")[:20]
    payload = [
        {
            "id": order.id,
            "customer_name": order.customer_name,
            "total": str(order.total),
            "status": order.status,
            "payment_status": (fetch_payment_record(order.id) or {}).get("status"),
            "shipping_status": (fetch_shipment_record(order.id) or {}).get("status"),
        }
        for order in orders
    ]
    return JsonResponse({"items": payload})


def order_detail_api(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=order_id)
    payment = fetch_payment_record(order.id)
    shipment = fetch_shipment_record(order.id)
    return JsonResponse(
        {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "shipping_address": order.shipping_address,
            "subtotal": str(order.subtotal),
            "shipping_fee": str(order.shipping_fee),
            "total": str(order.total),
            "status": order.status,
            "payment_status": payment["status"] if payment else None,
            "payment_reference": payment["transaction_reference"] if payment else None,
            "shipping_status": shipment["status"] if shipment else None,
            "tracking_code": shipment["tracking_code"] if shipment else None,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "unit_price": str(item.unit_price),
                    "quantity": item.quantity,
                    "line_total": str(item.line_total),
                }
                for item in order.items.all()
            ],
        }
    )
