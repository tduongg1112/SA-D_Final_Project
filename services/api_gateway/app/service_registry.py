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
        "name": "web-frontend",
        "type": "experience",
        "base_url": settings.web_frontend_url,
        "description": "React storefront shell served through the gateway for the rebuilt shopper and operator UI.",
        "status": "managed",
    },
    {
        "name": "commerce-service",
        "type": "transitional",
        "base_url": settings.commerce_service_url,
        "description": "Legacy Django storefront kept temporarily during the UI rebuild and service refactor.",
        "status": "managed",
    },
    {
        "name": "product-service",
        "type": "business",
        "base_url": settings.product_service_url,
        "description": "Dedicated product runtime for product and category APIs.",
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
    "web-frontend",
    "identity-service",
    "product-service",
    "cart-service",
    "ordering-service",
    "payment-service",
    "shipping-service",
    "ai-service",
    "api-gateway",
]
