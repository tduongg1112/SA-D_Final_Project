import os

import httpx
from config.product_media import enrich_cart_payload
from config.product_media import enrich_order_detail_payload
from config.product_media import enrich_product_detail_payload
from config.product_media import enrich_product_listing

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "").rstrip("/")
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


def _request(method, base_url, path, *, request=None, json=None, params=None, timeout=10.0):
    headers = {}
    if request is not None:
        headers["X-Session-Key"] = get_session_key(request)
    with httpx.Client(timeout=timeout) as client:
        response = client.request(method=method, url=f"{base_url}{path}", json=json, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def fetch_products(*, query="", category=""):
    if not PRODUCT_SERVICE_URL:
        return None
    params = {}
    if query:
        params["q"] = query
    if category:
        params["category"] = category
    try:
        return enrich_product_listing(_request("GET", PRODUCT_SERVICE_URL, "/api/products/", params=params or None))
    except httpx.HTTPError:
        return None


def fetch_product(slug):
    if not PRODUCT_SERVICE_URL:
        return None
    try:
        return enrich_product_detail_payload(_request("GET", PRODUCT_SERVICE_URL, f"/api/products/{slug}/"))
    except httpx.HTTPError:
        return None


def fetch_cart(request):
    if not CART_SERVICE_URL:
        return None
    try:
        return enrich_cart_payload(_request("GET", CART_SERVICE_URL, "/api/cart/", request=request))
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
        return enrich_order_detail_payload(_request("GET", ORDERING_SERVICE_URL, f"/api/orders/{order_id}/"))
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


def create_order(payload):
    if not ORDERING_SERVICE_URL:
        return None
    try:
        return _request("POST", ORDERING_SERVICE_URL, "/api/orders/checkout/", json=payload, timeout=20.0)
    except httpx.HTTPError:
        return None
