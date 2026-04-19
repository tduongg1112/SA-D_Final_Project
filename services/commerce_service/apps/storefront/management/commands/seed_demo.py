from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed demo users for the NovaMarket storefront shell."

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin12345")

        staff_user, _ = User.objects.get_or_create(
            username="staff",
            defaults={"email": "staff@example.com", "is_staff": True},
        )
        staff_user.is_staff = True
        staff_user.set_password("staff12345")
        staff_user.save()

        customer_user, _ = User.objects.get_or_create(
            username="customer",
            defaults={"email": "customer@example.com"},
        )
        customer_user.set_password("customer12345")
        customer_user.save()

        self.stdout.write(self.style.SUCCESS("Demo accounts seeded successfully."))
