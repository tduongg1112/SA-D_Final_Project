import os

import httpx

CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "").rstrip("/")
ORDERING_SERVICE_URL = os.getenv("ORDERING_SERVICE_URL", "").rstrip("/")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "").rstrip("/")
SHIPPING_SERVICE_URL = os.getenv("SHIPPING_SERVICE_URL", "").rstrip("/")


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    request.session.setdefault("cart_session_key", request.session.session_key)
    request.session.modified = True
    return request.session.session_key


def _request(method, base_url, path, *, request=None, json=None, timeout=10.0):
    headers = {}
    if request is not None:
        headers["X-Session-Key"] = get_session_key(request)
    with httpx.Client(timeout=timeout) as client:
        response = client.request(method=method, url=f"{base_url}{path}", json=json, headers=headers)
    response.raise_for_status()
    return response.json()


def fetch_cart(request):
    if not CART_SERVICE_URL:
        return None
    try:
        return _request("GET", CART_SERVICE_URL, "/api/cart/", request=request)
    except httpx.HTTPError:
        return None


def add_cart_item(request, product_id, quantity=1):
    if not CART_SERVICE_URL:
        return None
    try:
        return _request(
            "POST",
            CART_SERVICE_URL,
            "/api/cart/items/",
            request=request,
            json={"product_id": product_id, "quantity": quantity},
        )
    except httpx.HTTPError:
        return None


def update_cart_item(request, item_id, quantity):
    if not CART_SERVICE_URL:
        return None
    try:
        return _request(
            "POST",
            CART_SERVICE_URL,
            f"/api/cart/items/{item_id}/",
            request=request,
            json={"quantity": quantity},
        )
    except httpx.HTTPError:
        return None


def remove_cart_item(request, item_id):
    if not CART_SERVICE_URL:
        return None
    try:
        return _request("POST", CART_SERVICE_URL, f"/api/cart/items/{item_id}/remove/", request=request)
    except httpx.HTTPError:
        return None


def clear_cart(request):
    if not CART_SERVICE_URL:
        return None
    try:
        return _request("POST", CART_SERVICE_URL, "/api/cart/clear/", request=request)
    except httpx.HTTPError:
        return None


def fetch_order_detail(order_id):
    if not ORDERING_SERVICE_URL:
        return None
    try:
        return _request("GET", ORDERING_SERVICE_URL, f"/api/orders/{order_id}/")
    except httpx.HTTPError:
        return None


def fetch_orders():
    if not ORDERING_SERVICE_URL:
        return None
    try:
        return _request("GET", ORDERING_SERVICE_URL, "/api/orders/")
    except httpx.HTTPError:
        return None


def fetch_payments():
    if not PAYMENT_SERVICE_URL:
        return None
    try:
        return _request("GET", PAYMENT_SERVICE_URL, "/api/payments/")
    except httpx.HTTPError:
        return None


def fetch_shipments():
    if not SHIPPING_SERVICE_URL:
        return None
    try:
        return _request("GET", SHIPPING_SERVICE_URL, "/api/shipping/")
    except httpx.HTTPError:
        return None
