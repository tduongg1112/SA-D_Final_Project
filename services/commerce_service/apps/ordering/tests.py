from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Category, Product
from apps.ordering.models import Order


class OrderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Laptop", slug="laptop")
        cls.product = Product.objects.create(
            category=category,
            name="NovaBook Air 14",
            slug="novabook-air-14",
            brand="Nova",
            short_description="A lightweight laptop",
            description="Test description",
            price="19.90",
            stock_quantity=10,
        )

    def test_checkout_creates_order(self):
        self.client.post(reverse("cart:add", args=[self.product.id]))
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
        self.assertEqual(Order.objects.count(), 1)

# Create your tests here.
