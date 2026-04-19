import json
from decimal import Decimal
from urllib.parse import urlparse
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from app.main import app


class GatewaySmokeFlowTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.product = {
            "id": 1,
            "name": "NovaBook Flex 13",
            "slug": "novabook-flex-13",
            "absolute_url": "/products/novabook-flex-13/",
            "category": {
                "id": 1,
                "name": "Work Tech",
                "slug": "work-tech",
                "description": "Portable work tools and productivity essentials.",
            },
            "brand": "Nova",
            "short_description": "A lightweight laptop for study and focused work.",
            "description": "Slim form factor and reliable battery life.",
            "price": "18.90",
            "stock_quantity": 12,
            "featured": True,
            "status": "active",
            "status_label": "Active",
            "accent_color": "#EEF4FF",
            "is_in_stock": True,
        }
        self.state = {
            "products": {self.product["id"]: self.product},
            "carts": {},
            "orders": [],
            "payments": [],
            "shipments": [],
            "next_cart_item_id": 1,
            "next_order_id": 1,
        }

    def _money(self, value):
        return f"{Decimal(value):.2f}"

    def _cart_payload(self, session_key):
        cart = self.state["carts"].setdefault(session_key, {})
        items = list(cart.values())
        item_count = sum(item["quantity"] for item in items)
        subtotal = sum((Decimal(item["price"]) * item["quantity"] for item in items), Decimal("0.00"))
        shipping_fee = Decimal("5.00") if item_count else Decimal("0.00")
        return {
            "session_key": session_key,
            "item_count": item_count,
            "subtotal": self._money(subtotal),
            "shipping_fee": self._money(shipping_fee),
            "total": self._money(subtotal + shipping_fee),
            "items": [
                {
                    **item,
                    "line_total": self._money(Decimal(item["price"]) * item["quantity"]),
                }
                for item in items
            ],
        }

    def _json_body(self, content):
        if not content:
            return {}
        if isinstance(content, bytes):
            raw = content.decode("utf-8")
        else:
            raw = content
        return json.loads(raw)

    def _response(self, method, url, payload, status_code=200):
        request = httpx.Request(method=method, url=url)
        return httpx.Response(status_code=status_code, json=payload, request=request)

    def _fake_request(self):
        state = self.state

        async def fake_request(_client, method, url, content=None, headers=None, **kwargs):
            headers = headers or {}
            session_key = headers.get("x-session-key") or headers.get("X-Session-Key") or "anonymous"
            path = urlparse(url).path.rstrip("/") or "/"
            body = self._json_body(content)

            if path == "/api/products":
                return self._response(
                    method,
                    url,
                    {
                        "items": list(state["products"].values()),
                        "categories": [self.product["category"]],
                    },
                )

            if path == "/api/cart":
                return self._response(method, url, self._cart_payload(session_key))

            if path == "/api/cart/items" and method.upper() == "POST":
                product = state["products"][int(body["product_id"])]
                cart = state["carts"].setdefault(session_key, {})
                existing = next((item for item in cart.values() if item["product_id"] == product["id"]), None)
                quantity = int(body.get("quantity", 1))
                if existing is None:
                    item_id = state["next_cart_item_id"]
                    state["next_cart_item_id"] += 1
                    cart[item_id] = {
                        "id": item_id,
                        "product_id": product["id"],
                        "product": product["name"],
                        "product_slug": product["slug"],
                        "category": product["category"]["name"],
                        "brand": product["brand"],
                        "short_description": product["short_description"],
                        "accent_color": product["accent_color"],
                        "quantity": quantity,
                        "price": product["price"],
                    }
                else:
                    existing["quantity"] += quantity
                return self._response(method, url, self._cart_payload(session_key), status_code=201)

            if path == "/api/cart/clear" and method.upper() == "POST":
                state["carts"][session_key] = {}
                return self._response(method, url, self._cart_payload(session_key))

            if path == "/api/orders/checkout" and method.upper() == "POST":
                order_id = state["next_order_id"]
                state["next_order_id"] += 1
                subtotal = sum((Decimal(item["line_total"]) for item in body["items"]), Decimal("0.00"))
                payment = {
                    "id": order_id,
                    "order_id": order_id,
                    "provider": "MockPay",
                    "amount": self._money(subtotal + Decimal("5.00")),
                    "status": "paid",
                    "transaction_reference": f"PAY-{order_id:04d}",
                    "created_at": "2026-04-19T00:00:00+07:00",
                }
                shipment = {
                    "id": order_id,
                    "order_id": order_id,
                    "recipient_name": body["customer_name"],
                    "phone": body["customer_phone"],
                    "address": body["shipping_address"],
                    "method": "Standard delivery",
                    "status": "preparing",
                    "tracking_code": f"SHP-{order_id:04d}",
                    "created_at": "2026-04-19T00:00:00+07:00",
                }
                order = {
                    "id": order_id,
                    "customer_name": body["customer_name"],
                    "customer_email": body["customer_email"],
                    "customer_phone": body["customer_phone"],
                    "shipping_address": body["shipping_address"],
                    "subtotal": self._money(subtotal),
                    "shipping_fee": "5.00",
                    "total": self._money(subtotal + Decimal("5.00")),
                    "status": "confirmed",
                    "payment_status": payment["status"],
                    "payment_reference": payment["transaction_reference"],
                    "shipping_status": shipment["status"],
                    "tracking_code": shipment["tracking_code"],
                    "items": body["items"],
                }
                state["orders"].append(order)
                state["payments"].append(payment)
                state["shipments"].append(shipment)
                return self._response(
                    method,
                    url,
                    {
                        "id": order_id,
                        "status": order["status"],
                        "payment_status": payment["status"],
                        "shipping_status": shipment["status"],
                    },
                    status_code=201,
                )

            if path == "/api/orders":
                return self._response(
                    method,
                    url,
                    {
                        "items": [
                            {
                                "id": order["id"],
                                "customer_name": order["customer_name"],
                                "total": order["total"],
                                "status": order["status"],
                                "payment_status": order["payment_status"],
                                "shipping_status": order["shipping_status"],
                            }
                            for order in state["orders"]
                        ]
                    },
                )

            if path.startswith("/api/orders/"):
                order_id = int(path.split("/")[-1])
                order = next(order for order in state["orders"] if order["id"] == order_id)
                return self._response(method, url, order)

            if path == "/api/payments":
                return self._response(method, url, {"items": state["payments"]})

            if path == "/api/shipping":
                return self._response(method, url, {"items": state["shipments"]})

            return self._response(method, url, {"detail": f"Unhandled upstream path: {path}"}, status_code=404)

        return fake_request

    def test_gateway_smoke_checkout_flow(self):
        session_key = "gateway-smoke-session"
        with patch("app.proxy.httpx.AsyncClient.request", new=self._fake_request()):
            browse_response = self.client.get("/api/products/")
            self.assertEqual(browse_response.status_code, 200)
            self.assertEqual(browse_response.json()["items"][0]["slug"], self.product["slug"])
            self.assertIn("x-request-id", browse_response.headers)

            add_to_cart_response = self.client.post(
                "/api/cart/items/",
                json={"product_id": self.product["id"], "quantity": 2},
                headers={"X-Session-Key": session_key},
            )
            self.assertEqual(add_to_cart_response.status_code, 201)

            cart_response = self.client.get("/api/cart/", headers={"X-Session-Key": session_key})
            self.assertEqual(cart_response.status_code, 200)
            cart_payload = cart_response.json()
            self.assertEqual(cart_payload["item_count"], 2)
            self.assertEqual(cart_payload["total"], "42.80")

            checkout_response = self.client.post(
                "/api/orders/checkout/",
                json={
                    "customer_name": "Gateway Smoke User",
                    "customer_email": "smoke@example.com",
                    "customer_phone": "0123456789",
                    "shipping_address": "123 Gateway Street",
                    "note": "Smoke flow",
                    "items": [
                        {
                            "product_id": item["product_id"],
                            "product_name": item["product"],
                            "unit_price": item["price"],
                            "quantity": item["quantity"],
                            "line_total": item["line_total"],
                        }
                        for item in cart_payload["items"]
                    ],
                },
            )
            self.assertEqual(checkout_response.status_code, 201)
            checkout_payload = checkout_response.json()
            self.assertEqual(checkout_payload["payment_status"], "paid")
            self.assertEqual(checkout_payload["shipping_status"], "preparing")

            order_detail_response = self.client.get(f"/api/orders/{checkout_payload['id']}/")
            self.assertEqual(order_detail_response.status_code, 200)
            self.assertEqual(order_detail_response.json()["tracking_code"], "SHP-0001")

            payments_response = self.client.get("/api/payments/")
            self.assertEqual(payments_response.status_code, 200)
            self.assertEqual(payments_response.json()["items"][0]["order_id"], checkout_payload["id"])

            shipping_response = self.client.get("/api/shipping/")
            self.assertEqual(shipping_response.status_code, 200)
            self.assertEqual(shipping_response.json()["items"][0]["order_id"], checkout_payload["id"])
