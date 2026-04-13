from app.config import settings

LIVE_SERVICES = [
    {
        "name": "api-gateway",
        "type": "edge",
        "base_url": "self",
        "description": "Single public entry point, request routing, health aggregation, and gateway UI.",
        "status": "running",
    },
    {
        "name": "commerce-service",
        "type": "business",
        "base_url": settings.commerce_service_url,
        "description": "Storefront UI, cart flow, and the remaining consolidated business capabilities.",
        "status": "managed",
    },
    {
        "name": "catalog-service",
        "type": "business",
        "base_url": settings.catalog_service_url,
        "description": "Dedicated catalog runtime for product and category APIs.",
        "status": "managed",
    },
    {
        "name": "cart-service",
        "type": "business",
        "base_url": settings.cart_service_url,
        "description": "Dedicated cart runtime for cart state and cart APIs.",
        "status": "managed",
    },
    {
        "name": "ordering-service",
        "type": "business",
        "base_url": settings.ordering_service_url,
        "description": "Dedicated ordering runtime for order creation and order read models.",
        "status": "managed",
    },
    {
        "name": "payment-service",
        "type": "business",
        "base_url": settings.payment_service_url,
        "description": "Dedicated payment runtime for payment records and payment status APIs.",
        "status": "managed",
    },
    {
        "name": "shipping-service",
        "type": "business",
        "base_url": settings.shipping_service_url,
        "description": "Dedicated shipping runtime for shipment records and tracking APIs.",
        "status": "managed",
    },
    {
        "name": "ai-service",
        "type": "intelligence",
        "base_url": settings.ai_service_url,
        "description": "Recommendation and conversational shopping assistant.",
        "status": "managed",
    },
]

TARGET_SERVICE_MAP = [
    "identity-service",
    "catalog-service",
    "cart-service",
    "ordering-service",
    "payment-service",
    "shipping-service",
    "ai-service",
    "api-gateway",
]
