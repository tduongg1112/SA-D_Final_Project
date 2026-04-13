from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.proxy import proxy_request, service_health
from app.service_registry import LIVE_SERVICES, TARGET_SERVICE_MAP

app = FastAPI(title="TechStore API Gateway")
app.mount("/gateway/static", StaticFiles(directory="app/static"), name="gateway-static")
templates = Jinja2Templates(directory="app/templates")


@app.middleware("http")
async def attach_request_metadata(request: Request, call_next):
    request.state.request_id = uuid4().hex[:12]
    started_at = perf_counter()
    response = await call_next(request)
    response.headers["x-request-id"] = request.state.request_id
    response.headers["x-response-time-ms"] = f"{(perf_counter() - started_at) * 1000:.2f}"
    return response


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/gateway/health")
async def aggregated_health():
    checks = {
        "commerce-service": await service_health(settings.commerce_service_url),
        "catalog-service": await service_health(settings.catalog_service_url),
        "cart-service": await service_health(settings.cart_service_url),
        "ordering-service": await service_health(settings.ordering_service_url),
        "payment-service": await service_health(settings.payment_service_url),
        "shipping-service": await service_health(settings.shipping_service_url),
        "ai-service": await service_health(settings.ai_service_url),
    }
    return {
        "gateway": {"status": "healthy"},
        "services": checks,
    }


@app.get("/gateway/api/services")
async def service_overview():
    checks = await aggregated_health()
    return {
        "live_services": LIVE_SERVICES,
        "target_microservices": TARGET_SERVICE_MAP,
        "health": checks,
    }


@app.get("/gateway/", response_class=HTMLResponse)
async def gateway_dashboard(request: Request):
    health = await aggregated_health()
    return templates.TemplateResponse(
        request,
        "gateway/index.html",
        {
            "live_services": LIVE_SERVICES,
            "target_microservices": TARGET_SERVICE_MAP,
            "health": health["services"],
        },
    )


@app.api_route("/api/catalog/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_catalog_proxy(request: Request, path: str):
    return await proxy_request(request, settings.catalog_service_url, f"/api/catalog/{path}")


@app.api_route("/api/cart/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_cart_proxy(request: Request, path: str):
    return await proxy_request(request, settings.cart_service_url, f"/api/cart/{path}")


@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_orders_proxy(request: Request, path: str):
    return await proxy_request(request, settings.ordering_service_url, f"/api/orders/{path}")


@app.api_route("/api/ai/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_ai_proxy(request: Request, path: str):
    return await proxy_request(request, settings.ai_service_url, f"/api/ai/{path}")


@app.api_route("/api/payments/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_payments_proxy(request: Request, path: str):
    return await proxy_request(request, settings.payment_service_url, f"/api/payments/{path}")


@app.api_route("/api/shipping/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_shipping_proxy(request: Request, path: str):
    return await proxy_request(request, settings.shipping_service_url, f"/api/shipping/{path}")


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def storefront_proxy(request: Request, path: str):
    return await proxy_request(request, settings.commerce_service_url, path)
