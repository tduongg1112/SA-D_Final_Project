from django.test import TestCase
from django.urls import reverse

from apps.ordering.models import Order, OrderItem


class OrderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.order = Order.objects.create(
            customer_name="Test User",
            customer_email="user@example.com",
            customer_phone="0123456789",
            shipping_address="123 Test Street",
            subtotal="10.00",
            shipping_fee="5.00",
            total="15.00",
        )
        OrderItem.objects.create(
            order=cls.order,
            product_name="NovaBook Air 14",
            unit_price="10.00",
            quantity=1,
            line_total="10.00",
        )

    def test_orders_api_returns_seeded_order(self):
        response = self.client.get(reverse("api-orders"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)
        self.assertIsNone(response.json()["items"][0]["payment_status"])

    def test_order_detail_api_returns_order_payload(self):
        response = self.client.get(reverse("api-order-detail", args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["customer_name"], "Test User")

    def test_checkout_api_creates_new_order(self):
        response = self.client.post(
            reverse("api-order-checkout"),
            data={
                "customer_name": "Checkout User",
                "customer_email": "checkout@example.com",
                "customer_phone": "0999999999",
                "shipping_address": "456 Checkout Road",
                "note": "Leave at reception",
                "items": [
                    {
                        "product_id": 10,
                        "product_name": "QuietPods Studio",
                        "unit_price": "2.90",
                        "quantity": 1,
                        "line_total": "2.90",
                    }
                ],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 2)
