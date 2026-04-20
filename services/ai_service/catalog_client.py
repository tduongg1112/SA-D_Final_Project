from __future__ import annotations

from collections.abc import Iterable

import httpx

from app_config import Settings
from knowledge_base import PRODUCT_KNOWLEDGE
from text_utils import tokenize


def normalize_product(payload: dict, *, fallback_score: float = 0.0, reason: str = "") -> dict:
    category = payload.get("category") or {}
    return {
        "id": payload.get("id"),
        "slug": payload["slug"],
        "name": payload["name"],
        "brand": payload.get("brand", "NovaMarket"),
        "category_name": category.get("name") or payload.get("category_name", "General"),
        "category_slug": category.get("slug") or payload.get("category_slug", "general"),
        "short_description": payload.get("short_description") or payload.get("summary", ""),
        "price": str(payload.get("price", "0.00")),
        "absolute_url": payload.get("absolute_url") or f"/products/{payload['slug']}",
        "accent_color": payload.get("accent_color", "#EEF4FF"),
        "featured": bool(payload.get("featured", False)),
        "reason": reason,
        "score": fallback_score,
        "tags": payload.get("tags", []),
        "complements": payload.get("complements", []),
        "summary": payload.get("summary", payload.get("short_description", "")),
    }


class CatalogClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._fallback_products = [normalize_product(product) for product in PRODUCT_KNOWLEDGE]

    async def fetch_catalog(self, query: str = "", category_slug: str = "") -> list[dict]:
        params = {}
        if query.strip():
            params["q"] = query.strip()
        if category_slug.strip():
            params["category"] = category_slug.strip()

        target = f"{self.settings.product_service_url.rstrip('/')}/api/products/"
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.get(target, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError:
            return self._fallback_search(query=query, category_slug=category_slug)

        normalized_items = [normalize_product(item) for item in payload.get("items", [])]
        if normalized_items:
            return normalized_items

        if query.strip() or category_slug.strip():
            return self._fallback_search(query=query, category_slug=category_slug)

        return normalized_items

    def _fallback_search(self, query: str = "", category_slug: str = "") -> list[dict]:
        query_terms = tokenize(query)
        results: list[tuple[float, dict]] = []
        for product in self._fallback_products:
            searchable = " ".join(
                [
                    product["name"],
                    product["brand"],
                    product["short_description"],
                    product.get("summary", ""),
                    " ".join(product.get("tags", [])),
                ]
            ).lower()
            if category_slug and product["category_slug"] != category_slug:
                continue

            overlap = len(query_terms & tokenize(searchable))
            if query_terms and overlap == 0:
                continue
            score = float(overlap)
            if category_slug and product["category_slug"] == category_slug:
                score += 2.0
            if product.get("featured"):
                score += 0.25
            results.append((score, product))

        if results:
            results.sort(
                key=lambda item: (
                    -item[0],
                    item[1]["name"],
                )
            )
            return [product for _, product in results]

        if category_slug:
            category_matches = [product for product in self._fallback_products if product["category_slug"] == category_slug]
            if category_matches:
                return category_matches

        return list(self._fallback_products)

    def get_fallback_products(self) -> list[dict]:
        return list(self._fallback_products)

    def build_index(self, products: Iterable[dict]) -> dict[str, dict]:
        return {product["slug"]: product for product in products}
