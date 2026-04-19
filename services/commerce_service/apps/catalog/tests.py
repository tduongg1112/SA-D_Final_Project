from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class CatalogTests(TestCase):
    payload = {
        "items": [
            {
                "id": 1,
                "name": "NovaBook Air 14",
                "slug": "novabook-air-14",
                "absolute_url": "/products/novabook-air-14/",
                "category": {"name": "Laptop", "slug": "laptop", "description": ""},
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
        ],
        "categories": [{"name": "Laptop", "slug": "laptop", "description": ""}],
    }

    def test_catalog_api_returns_items(self):
        with patch("apps.catalog.views.fetch_products", return_value=self.payload):
            response = self.client.get(reverse("api-product-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

# Create your tests here.
