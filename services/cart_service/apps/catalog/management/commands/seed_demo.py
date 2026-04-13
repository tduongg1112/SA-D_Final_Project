from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Seed demo data for TechStore MVP."

    def handle(self, *args, **options):
        categories = [
            {
                "name": "Laptops",
                "slug": "laptop",
                "description": "Laptops for study, office work, and creative workflows.",
            },
            {
                "name": "Accessories",
                "slug": "phu-kien",
                "description": "Headphones, keyboards, mice, and desk setup essentials.",
            },
            {
                "name": "Displays",
                "slug": "man-hinh",
                "description": "Display products designed for long work sessions and balanced visuals.",
            },
            {
                "name": "Networking",
                "slug": "thiet-bi-mang",
                "description": "Routers and connectivity devices for stable study and work setups.",
            },
        ]
        for category in categories:
            Category.objects.update_or_create(slug=category["slug"], defaults=category)

        products = [
            {
                "category_slug": "laptop",
                "name": "NovaBook Air 14",
                "slug": "novabook-air-14",
                "brand": "Nova",
                "short_description": "A lightweight laptop for students and office users.",
                "description": "Slim form factor, reliable battery life, and a balanced setup for study and mobile work.",
                "price": "19.90",
                "stock_quantity": 14,
                "featured": True,
                "accent_color": "#EEF4FF",
            },
            {
                "category_slug": "laptop",
                "name": "NovaBook Pro 16",
                "slug": "novabook-pro-16",
                "brand": "Nova",
                "short_description": "Higher performance for coding and heavy multitasking.",
                "description": "Large display, stronger performance, and enough room for development and multi-window workflows.",
                "price": "32.50",
                "stock_quantity": 8,
                "featured": True,
                "accent_color": "#F3F1FF",
            },
            {
                "category_slug": "phu-kien",
                "name": "QuietPods Studio",
                "slug": "quietpods-studio",
                "brand": "Orbit",
                "short_description": "Noise-cancelling headphones for remote work.",
                "description": "Balanced audio, comfortable long-wear fit, and reliable call clarity for hybrid work.",
                "price": "2.90",
                "stock_quantity": 35,
                "featured": True,
                "accent_color": "#EFF8F1",
            },
            {
                "category_slug": "phu-kien",
                "name": "FlowKeys Minimal",
                "slug": "flowkeys-minimal",
                "brand": "Flow",
                "short_description": "A minimal keyboard for a clean desk setup.",
                "description": "Neutral design, soft typing feel, and a tidy visual fit for light workspaces.",
                "price": "1.80",
                "stock_quantity": 24,
                "featured": False,
                "accent_color": "#FFF6E8",
            },
            {
                "category_slug": "man-hinh",
                "name": "ClearView 27 QHD",
                "slug": "clearview-27-qhd",
                "brand": "Clear",
                "short_description": "A calm 27-inch display for study and focused work.",
                "description": "QHD resolution, stable color output, and comfortable long-session viewing.",
                "price": "6.40",
                "stock_quantity": 11,
                "featured": True,
                "accent_color": "#EEF7FF",
            },
            {
                "category_slug": "thiet-bi-mang",
                "name": "AeroMesh Home",
                "slug": "aeromesh-home",
                "brand": "Aero",
                "short_description": "A mesh router for apartments and small homes.",
                "description": "Easy setup, reliable coverage, and a stable signal for classes, calls, and streaming.",
                "price": "3.20",
                "stock_quantity": 16,
                "featured": False,
                "accent_color": "#F4F5FF",
            },
        ]
        for data in products:
            category = Category.objects.get(slug=data.pop("category_slug"))
            Product.objects.update_or_create(
                slug=data["slug"],
                defaults={**data, "category": category},
            )

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

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
