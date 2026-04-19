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
            patch("apps.ordering.views.create_order", return_value={"id": 99}),
            patch("apps.ordering.views.clear_cart", return_value={}),
        ):
            response = self.client.post(
                reverse("ordering:checkout"),
                {
                    "customer_name": "Test User",
                    "customer_email": "user@example.com",
                    "customer_phone": "0123456789",
                    "shipping_address": "123 Test Street",
                    "note": "Please deliver soon",
                },
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("ordering:success", args=[99]))

# Create your tests here.
