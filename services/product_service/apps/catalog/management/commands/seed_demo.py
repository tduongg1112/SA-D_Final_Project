from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Seed demo data for the NovaMarket multi-category storefront."

    def handle(self, *args, **options):
        categories = [
            {
                "name": "Work Tech",
                "slug": "work-tech",
                "description": "Portable work tools, desk gear, and focused productivity essentials.",
            },
            {
                "name": "Home Living",
                "slug": "home-living",
                "description": "Soft home accents and compact items for calmer living spaces.",
            },
            {
                "name": "Kitchen Dining",
                "slug": "kitchen-dining",
                "description": "Everyday kitchen tools and simple dining accessories.",
            },
            {
                "name": "Wellness",
                "slug": "wellness",
                "description": "Movement, hydration, and self-care products for daily routines.",
            },
            {
                "name": "Travel Everyday",
                "slug": "travel-everyday",
                "description": "Bags and carry pieces for commuting, short trips, and daily errands.",
            },
            {
                "name": "Beauty Care",
                "slug": "beauty-care",
                "description": "Compact beauty and personal care products for everyday use.",
            },
        ]
        for category in categories:
            Category.objects.update_or_create(slug=category["slug"], defaults=category)

        products = [
            {
                "category_slug": "work-tech",
                "name": "NovaBook Flex 13",
                "slug": "novabook-flex-13",
                "brand": "Nova",
                "short_description": "A lightweight laptop for study, travel, and focused work.",
                "description": "Slim form factor, reliable battery life, and a balanced setup for writing, planning, and mobile work.",
                "price": "18.90",
                "stock_quantity": 12,
                "featured": True,
                "accent_color": "#EEF4FF",
            },
            {
                "category_slug": "work-tech",
                "name": "Luma Desk Light",
                "slug": "luma-desk-light",
                "brand": "Luma",
                "short_description": "An adjustable desk lamp for compact work corners.",
                "description": "Soft illumination, compact footprint, and a clean silhouette for study desks and small home offices.",
                "price": "2.40",
                "stock_quantity": 26,
                "featured": False,
                "accent_color": "#FFF6E8",
            },
            {
                "category_slug": "home-living",
                "name": "CloudRest Throw",
                "slug": "cloudrest-throw",
                "brand": "Hush",
                "short_description": "A soft throw blanket for reading nooks and sofas.",
                "description": "Lightweight warmth, neutral texture, and easy styling for a brighter living room or bedroom corner.",
                "price": "1.90",
                "stock_quantity": 18,
                "featured": False,
                "accent_color": "#F6F1FF",
            },
            {
                "category_slug": "home-living",
                "name": "AromaNest Diffuser",
                "slug": "aromanest-diffuser",
                "brand": "Nest",
                "short_description": "A ceramic diffuser for small rooms and calmer evenings.",
                "description": "Quiet mist output, soft matte finish, and a compact shape that fits desks, shelves, and bedside tables.",
                "price": "2.70",
                "stock_quantity": 20,
                "featured": True,
                "accent_color": "#EFF8F1",
            },
            {
                "category_slug": "kitchen-dining",
                "name": "BrewMate Press",
                "slug": "brewmate-press",
                "brand": "BrewMate",
                "short_description": "A compact French press for slower morning coffee.",
                "description": "Easy-grip handle, clear glass body, and a compact size for one or two cups at home.",
                "price": "2.20",
                "stock_quantity": 22,
                "featured": False,
                "accent_color": "#FFF3EC",
            },
            {
                "category_slug": "kitchen-dining",
                "name": "SliceBoard Duo",
                "slug": "sliceboard-duo",
                "brand": "Hearth",
                "short_description": "A bamboo cutting board set for everyday meal prep.",
                "description": "Two versatile sizes, warm natural tone, and an easy fit for compact kitchens.",
                "price": "1.60",
                "stock_quantity": 17,
                "featured": False,
                "accent_color": "#F5F0E8",
            },
            {
                "category_slug": "wellness",
                "name": "CoreBalance Mat",
                "slug": "corebalance-mat",
                "brand": "Core",
                "short_description": "A non-slip yoga mat for stretching and light training.",
                "description": "Soft cushioning, stable grip, and a simple finish that works for home workouts and warm-ups.",
                "price": "2.10",
                "stock_quantity": 21,
                "featured": True,
                "accent_color": "#EEF7FF",
            },
            {
                "category_slug": "wellness",
                "name": "PureSip Bottle",
                "slug": "puresip-bottle",
                "brand": "PureSip",
                "short_description": "An insulated bottle for water, tea, and daily routines.",
                "description": "Clean shape, comfortable grip, and all-day portability for work, class, or gym sessions.",
                "price": "1.35",
                "stock_quantity": 30,
                "featured": False,
                "accent_color": "#F0FAFF",
            },
            {
                "category_slug": "travel-everyday",
                "name": "Transit Weekender",
                "slug": "transit-weekender",
                "brand": "Route",
                "short_description": "A compact travel bag for overnights and short city trips.",
                "description": "Structured body, soft handles, and enough space for clothing, toiletries, and small daily essentials.",
                "price": "3.40",
                "stock_quantity": 15,
                "featured": True,
                "accent_color": "#F2F4FF",
            },
            {
                "category_slug": "travel-everyday",
                "name": "LinenCarry Tote",
                "slug": "linencarry-tote",
                "brand": "Linen",
                "short_description": "A minimal tote bag for markets, errands, and daily carry.",
                "description": "Light structure, soft fabric blend, and a relaxed form suited to short everyday trips.",
                "price": "1.10",
                "stock_quantity": 28,
                "featured": False,
                "accent_color": "#F9F4EE",
            },
            {
                "category_slug": "beauty-care",
                "name": "GlowMirror Mini",
                "slug": "glowmirror-mini",
                "brand": "Glow",
                "short_description": "A portable LED mirror for desks, travel, and touch-ups.",
                "description": "Clean silhouette, soft integrated light, and a compact size that slips easily into a bag.",
                "price": "1.75",
                "stock_quantity": 19,
                "featured": False,
                "accent_color": "#FFF1F5",
            },
            {
                "category_slug": "beauty-care",
                "name": "CalmSkin Set",
                "slug": "calmskin-set",
                "brand": "Calm",
                "short_description": "A gentle skincare starter set for simple routines.",
                "description": "A balanced starter bundle designed for hydration, light cleansing, and a low-friction morning routine.",
                "price": "2.95",
                "stock_quantity": 14,
                "featured": True,
                "accent_color": "#F3F8F3",
            },
        ]
        for data in products:
            category = Category.objects.get(slug=data.pop("category_slug"))
            Product.objects.update_or_create(
                slug=data["slug"],
                defaults={**data, "category": category},
            )

        active_slugs = [product["slug"] for product in products]
        Product.objects.exclude(slug__in=active_slugs).update(
            status=Product.Status.DRAFT,
            featured=False,
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
