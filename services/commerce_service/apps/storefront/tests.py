from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class StorefrontTests(TestCase):
    def test_homepage_renders(self):
        with patch(
            "apps.storefront.views.fetch_products",
            return_value={
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
                        "featured": True,
                        "status": "active",
                        "status_label": "Active",
                        "accent_color": "#EEF4FF",
                        "is_in_stock": True,
                    }
                ],
                "categories": [{"name": "Laptop", "slug": "laptop", "description": ""}],
            },
        ):
            response = self.client.get(reverse("storefront:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NovaMarket")

# Create your tests here.
