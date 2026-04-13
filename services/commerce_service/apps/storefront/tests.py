from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Category, Product


class StorefrontTests(TestCase):
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
            featured=True,
        )

    def test_homepage_renders(self):
        response = self.client.get(reverse("storefront:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TechStore")

# Create your tests here.
