from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.cart.models import Cart, CartItem


class CartTests(TestCase):
    product_snapshot = {
        "id": 1,
        "name": "NovaBook Air 14",
        "slug": "novabook-air-14",
        "category": {"name": "Laptops", "slug": "laptop", "description": ""},
        "brand": "Nova",
        "short_description": "A lightweight laptop",
        "description": "Test description",
        "price": "19.90",
        "stock_quantity": 10,
        "featured": False,
        "status": "active",
        "status_label": "Active",
        "accent_color": "#EEF4FF",
        "is_in_stock": True,
    }

    def test_cart_api_returns_cart_state(self):
        session = self.client.session
        session.save()
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(
            cart=cart,
            product_id=1,
            product_slug="novabook-air-14",
            product_name="NovaBook Air 14",
            category_name="Laptops",
            brand="Nova",
            short_description="A lightweight laptop",
            accent_color="#EEF4FF",
            unit_price="19.90",
            quantity=2,
        )
        response = self.client.get(reverse("api-cart"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["item_count"], 2)

    def test_add_item_api_creates_cart_item(self):
        session = self.client.session
        session.save()
        with patch("apps.cart.views.fetch_product_snapshot", return_value=self.product_snapshot):
            response = self.client.post(
                reverse("api-cart-add-item"),
                data={"product_id": 1, "quantity": 1},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["item_count"], 1)

    def test_clear_cart_api_removes_all_items(self):
        session = self.client.session
        session.save()
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(
            cart=cart,
            product_id=1,
            product_slug="novabook-air-14",
            product_name="NovaBook Air 14",
            category_name="Laptops",
            brand="Nova",
            short_description="A lightweight laptop",
            accent_color="#EEF4FF",
            unit_price="19.90",
            quantity=2,
        )
        response = self.client.post(reverse("api-cart-clear"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["item_count"], 0)
