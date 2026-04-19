from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class CartTests(TestCase):
    def test_add_to_cart_keeps_session_for_service_backed_cart(self):
        response_payload = Mock()
        response_payload.raise_for_status.return_value = None
        response_payload.json.return_value = {"item_count": 1}

        with (
            patch("config.service_clients.CART_SERVICE_URL", "http://cart-service:8003"),
            patch("config.service_clients.httpx.Client.request", return_value=response_payload) as request_mock,
        ):
            response = self.client.post(reverse("cart:add", args=[1]))

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
