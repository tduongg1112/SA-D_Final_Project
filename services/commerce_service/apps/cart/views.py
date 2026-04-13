from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.cart.models import CartItem
from apps.cart.utils import get_or_create_cart
from apps.cart.utils import serialize_cart
from apps.catalog.models import Product
from apps.ordering.forms import CheckoutForm
from config.service_clients import add_cart_item
from config.service_clients import fetch_cart
from config.service_clients import remove_cart_item
from config.service_clients import update_cart_item


def cart_detail(request):
    cart = fetch_cart(request)
    if cart is None:
        cart = get_or_create_cart(request)
        cart = cart.__class__.objects.prefetch_related("items__product__category").get(pk=cart.pk)
        cart = serialize_cart(cart)
    return render(
        request,
        "pages/cart/detail.html",
        {"cart": cart, "checkout_form": CheckoutForm()},
    )


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status=Product.Status.ACTIVE)
    if add_cart_item(request, product.id, 1) is None:
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
    return redirect("cart:detail")


@require_POST
def update_item(request, item_id):
    quantity = max(int(request.POST.get("quantity", 1)), 1)
    if update_cart_item(request, item_id, quantity) is None:
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem.objects.select_related("product"), pk=item_id, cart=cart)
        item.quantity = quantity
        item.save(update_fields=["quantity"])
    return redirect("cart:detail")


@require_POST
def remove_item(request, item_id):
    if remove_cart_item(request, item_id) is None:
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
    return redirect("cart:detail")


def cart_api(request):
    payload = fetch_cart(request)
    if payload is None:
        cart = get_or_create_cart(request)
        payload = serialize_cart(cart)
    return JsonResponse(payload)
