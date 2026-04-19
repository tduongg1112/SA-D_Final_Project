from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def test_dashboard_renders_with_remote_data(self):
        staff_user = User.objects.create_user(
            username="staff",
            password="staff12345",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        with (
            patch("apps.dashboard.views.fetch_products", return_value={"items": [{"id": 1}]}),
            patch("apps.dashboard.views.fetch_orders", return_value={"items": [{"id": 1, "customer_name": "Test", "total": "10.00", "payment_status": "paid", "shipping_status": "preparing"}]}),
            patch("apps.dashboard.views.fetch_payments", return_value={"items": [{"status": "paid"}]}),
            patch("apps.dashboard.views.fetch_shipments", return_value={"items": [{"status": "preparing"}]}),
        ):
            response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Operations in one bright analytics workspace.")
