from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    commerce_service_url: str = os.getenv("COMMERCE_SERVICE_URL", "http://commerce-service:8000")
    product_service_url: str = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8010")
    cart_service_url: str = os.getenv("CART_SERVICE_URL", "http://cart-service:8030")
    ordering_service_url: str = os.getenv("ORDERING_SERVICE_URL", "http://ordering-service:8020")
    payment_service_url: str = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8040")
    shipping_service_url: str = os.getenv("SHIPPING_SERVICE_URL", "http://shipping-service:8050")
    ai_service_url: str = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")
    request_timeout_seconds: float = float(os.getenv("GATEWAY_TIMEOUT", "20"))


settings = Settings()
