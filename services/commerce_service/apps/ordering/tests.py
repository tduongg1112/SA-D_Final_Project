from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class OrderingTests(TestCase):
    cart_payload = {
        "items": [
            {
                "id": 1,
                "product_id": 1,
                "product": "NovaBook Air 14",
                "product_slug": "novabook-air-14",
                "category": "Laptop",
                "brand": "Nova",
                "short_description": "A lightweight laptop",
                "accent_color": "#EEF4FF",
                "quantity": 1,
                "price": "19.90",
                "line_total": "19.90",
            }
        ],
        "item_count": 1,
        "subtotal": "19.90",
        "shipping_fee": "5.00",
        "total": "24.90",
    }

    def test_checkout_creates_order(self):
        with (
            patch("apps.ordering.views.fetch_cart", return_value=self.cart_payload),
            patch("apps.ordering.views.create_order", return_value={"id": 99}) as create_order,
            patch("apps.ordering.views.clear_cart", return_value={}),
        ):
            response = self.client.post(reverse("ordering:checkout"), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("ordering:success", args=[99]))
        payload = create_order.call_args.args[0]
        self.assertEqual(payload["customer_name"], "NovaMarket Demo")
        self.assertEqual(payload["customer_email"], "demo@novamarket.local")
        self.assertTrue(payload["shipping_address"].startswith("Demo checkout profile"))

# Create your tests here.
