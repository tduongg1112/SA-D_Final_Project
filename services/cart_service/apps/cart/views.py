import json
import os

import httpx
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.cart.models import CartItem
from apps.cart.utils import get_or_create_cart

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "").rstrip("/")


def fetch_product_snapshot(product_id):
    if not PRODUCT_SERVICE_URL:
        return None

    try:
        response = httpx.get(f"{PRODUCT_SERVICE_URL}/api/products/id/{product_id}/", timeout=5.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return False
        return None
    except httpx.HTTPError:
        return None
    return response.json()


def resolve_cart(request):
    session_key = request.headers.get("X-Session-Key") or request.GET.get("session_key")
    if session_key:
        cart, _ = get_or_create_cart(request).__class__.objects.get_or_create(session_key=session_key)
        return cart
    return get_or_create_cart(request)


def serialize_cart(cart):
    return {
        "session_key": cart.session_key,
        "item_count": cart.item_count,
        "subtotal": str(cart.subtotal),
        "shipping_fee": str(cart.shipping_fee),
        "total": str(cart.total),
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product": item.product_name,
                "product_slug": item.product_slug,
                "category": item.category_name,
                "brand": item.brand,
                "short_description": item.short_description,
                "accent_color": item.accent_color,
                "quantity": item.quantity,
                "price": str(item.unit_price),
                "line_total": str(item.line_total),
            }
            for item in cart.items.all()
        ],
    }


def cart_api(request):
    cart = resolve_cart(request)
    return JsonResponse(serialize_cart(cart))


@csrf_exempt
def clear_cart_api(request):
    if request.method not in {"DELETE", "POST"}:
        return JsonResponse({"detail": "Method not allowed."}, status=405)
    cart = resolve_cart(request)
    cart.items.all().delete()
    return JsonResponse(serialize_cart(cart))


@csrf_exempt
def add_item_api(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    cart = resolve_cart(request)
    product_id = int(payload.get("product_id", 0))
    product = fetch_product_snapshot(product_id)
    if product is False:
        return JsonResponse({"detail": "Product not found."}, status=404)
    if product is None:
        return JsonResponse({"detail": "Product service is unavailable."}, status=502)

    quantity = max(int(payload.get("quantity", 1)), 1)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product["id"],
        defaults={
            "product_slug": product["slug"],
            "product_name": product["name"],
            "category_name": product["category"]["name"],
            "brand": product["brand"],
            "short_description": product["short_description"],
            "accent_color": product["accent_color"],
            "unit_price": product["price"],
        },
    )
    cart_item.product_slug = product["slug"]
    cart_item.product_name = product["name"]
    cart_item.category_name = product["category"]["name"]
    cart_item.brand = product["brand"]
    cart_item.short_description = product["short_description"]
    cart_item.accent_color = product["accent_color"]
    cart_item.unit_price = product["price"]
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()
    return JsonResponse(serialize_cart(cart), status=201)


@csrf_exempt
def update_item_api(request, item_id):
    if request.method not in {"PATCH", "POST"}:
        return JsonResponse({"detail": "Method not allowed."}, status=405)
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else request.POST.dict()
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    cart = resolve_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.quantity = max(int(payload.get("quantity", 1)), 1)
    item.save(update_fields=["quantity"])
    return JsonResponse(serialize_cart(cart))


@csrf_exempt
def remove_item_api(request, item_id):
    if request.method not in {"DELETE", "POST"}:
        return JsonResponse({"detail": "Method not allowed."}, status=405)
    cart = resolve_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    return JsonResponse(serialize_cart(cart))
