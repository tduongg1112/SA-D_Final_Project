from apps.cart.models import Cart


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    request.session.setdefault("cart_session_key", request.session.session_key)
    request.session.modified = True
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


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
            for item in cart.items.select_related("product__category")
        ],
    }
