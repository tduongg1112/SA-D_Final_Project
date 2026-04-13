import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.cart.models import CartItem
from apps.cart.utils import get_or_create_cart
from apps.catalog.models import Product


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
                "product": item.product.name,
                "product_slug": item.product.slug,
                "category": item.product.category.name,
                "brand": item.product.brand,
                "short_description": item.product.short_description,
                "accent_color": item.product.accent_color,
                "quantity": item.quantity,
                "price": str(item.product.price),
                "line_total": str(item.line_total),
            }
            for item in cart.items.select_related("product")
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
    product = get_object_or_404(Product, pk=payload.get("product_id"), status=Product.Status.ACTIVE)
    quantity = max(int(payload.get("quantity", 1)), 1)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
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
    item = get_object_or_404(CartItem.objects.select_related("product"), pk=item_id, cart=cart)
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
