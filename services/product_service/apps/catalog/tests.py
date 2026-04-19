from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Category, Product


class CatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Laptop", slug="laptop")
        Product.objects.create(
            category=category,
            name="NovaBook Air 14",
            slug="novabook-air-14",
            brand="Nova",
            short_description="A lightweight laptop",
            description="Test description",
            price="19.90",
            stock_quantity=10,
        )

    def test_catalog_api_returns_items(self):
        response = self.client.get(reverse("api-product-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_product_detail_api_returns_related_products(self):
        response = self.client.get(reverse("api-product-detail", args=["novabook-air-14"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["product"]["slug"], "novabook-air-14")

    def test_reserve_stock_api_decrements_inventory(self):
        response = self.client.post(
            reverse("api-product-stock-reserve"),
            data={"items": [{"product_id": 1, "quantity": 2}]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["remaining_stock"], 8)

# Create your tests here.
