from django.test import TestCase
from django.urls import reverse

from apps.shipping.models import Shipment


class ShippingServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.shipment = Shipment.objects.create(
            order_id=101,
            recipient_name="Test User",
            phone="0123456789",
            address="123 Test Street",
            method="Standard delivery",
            status=Shipment.Status.PREPARING,
            tracking_code="SHP-TEST-001",
        )

    def test_shipments_api_returns_seeded_shipment(self):
        response = self.client.get(reverse("api-shipments"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_shipment_detail_api_returns_order_shipment(self):
        response = self.client.get(reverse("api-shipment-detail", args=[self.shipment.order_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tracking_code"], "SHP-TEST-001")

    def test_shipments_api_creates_shipment_record(self):
        response = self.client.post(
            reverse("api-shipments"),
            data={
                "order_id": 202,
                "recipient_name": "Checkout User",
                "phone": "0999999999",
                "address": "456 Checkout Road",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Shipment.objects.count(), 2)
