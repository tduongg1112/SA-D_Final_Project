from django.test import TestCase
from django.urls import reverse

from apps.payments.models import PaymentRecord


class PaymentServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.payment = PaymentRecord.objects.create(
            order_id=101,
            provider="MockPay",
            amount="99.90",
            status=PaymentRecord.Status.PAID,
            transaction_reference="PAY-TEST-001",
        )

    def test_payments_api_returns_seeded_payment(self):
        response = self.client.get(reverse("api-payments"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_payment_detail_api_returns_order_payment(self):
        response = self.client.get(reverse("api-payment-detail", args=[self.payment.order_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["transaction_reference"], "PAY-TEST-001")

    def test_payments_api_creates_payment_record(self):
        response = self.client.post(
            reverse("api-payments"),
            data={"order_id": 202, "amount": "149.00", "status": PaymentRecord.Status.PAID},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PaymentRecord.objects.count(), 2)
