from django.test import TestCase
from django.urls import reverse

from apps.cart.models import Cart, CartItem
from apps.catalog.models import Category, Product


class CartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Laptops", slug="laptop")
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

    def test_cart_api_returns_cart_state(self):
        session = self.client.session
        session.save()
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        response = self.client.get(reverse("api-cart"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["item_count"], 2)

    def test_add_item_api_creates_cart_item(self):
        session = self.client.session
        session.save()
        response = self.client.post(
            reverse("api-cart-add-item"),
            data={"product_id": self.product.id, "quantity": 1},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["item_count"], 1)

    def test_clear_cart_api_removes_all_items(self):
        session = self.client.session
        session.save()
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        response = self.client.post(reverse("api-cart-clear"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["item_count"], 0)
