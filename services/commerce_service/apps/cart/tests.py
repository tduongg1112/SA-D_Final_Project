from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Category, Product


class CartTests(TestCase):
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

    def test_add_to_cart_keeps_session_for_service_backed_cart(self):
        response_payload = Mock()
        response_payload.raise_for_status.return_value = None
        response_payload.json.return_value = {"item_count": 1}

        with (
            patch("config.service_clients.CART_SERVICE_URL", "http://cart-service:8003"),
            patch("config.service_clients.httpx.Client.request", return_value=response_payload) as request_mock,
        ):
            response = self.client.post(reverse("cart:add", args=[self.product.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.session_key)
        self.assertEqual(
            self.client.session["cart_session_key"],
            self.client.session.session_key,
        )
        self.assertIn(settings.SESSION_COOKIE_NAME, self.client.cookies)
        self.assertEqual(
            request_mock.call_args.kwargs["headers"]["X-Session-Key"],
            self.client.session.session_key,
        )
