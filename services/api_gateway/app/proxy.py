from typing import Iterable

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import Response

from app.config import settings

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def sanitize_headers(headers: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers
        if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "set-cookie"
    }


async def proxy_request(request: Request, destination_base_url: str, destination_path: str = "") -> Response:
    query = request.url.query
    target_url = f"{destination_base_url.rstrip('/')}/{destination_path.lstrip('/')}"
    if query:
        target_url = f"{target_url}?{query}"

    body = await request.body()
    forwarded_headers = sanitize_headers(request.headers.items())
    forwarded_headers["x-gateway-service"] = "api-gateway"
    forwarded_headers["x-request-id"] = getattr(request.state, "request_id", "unknown")

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            upstream = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=forwarded_headers,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Gateway could not reach upstream service: {exc}") from exc

    response_headers = sanitize_headers(upstream.headers.items())
    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )
    for cookie in upstream.headers.get_list("set-cookie"):
        response.raw_headers.append((b"set-cookie", cookie.encode("latin-1")))
    return response


async def service_health(service_url: str, path: str = "/health") -> dict:
    target = f"{service_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(target)
        return {
            "status": "healthy" if response.is_success else "degraded",
            "status_code": response.status_code,
            "url": target,
        }
    except httpx.HTTPError as exc:
        return {
            "status": "unreachable",
            "status_code": None,
            "url": target,
            "error": str(exc),
        }
