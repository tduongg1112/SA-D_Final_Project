from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render

from config.service_clients import fetch_product
from config.service_clients import fetch_products


def product_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    payload = fetch_products(query=query, category=category_slug) or {"items": [], "categories": []}
    return render(
        request,
        "pages/catalog/list.html",
        {
            "products": payload["items"],
            "categories": payload["categories"],
            "active_category": category_slug,
            "query": query,
        },
    )


def product_detail(request, slug):
    payload = fetch_product(slug)
    if payload is None:
        raise Http404("Product is unavailable.")
    return render(
        request,
        "pages/catalog/detail.html",
        {
            "product": payload["product"],
            "related_products": payload["related_products"],
        },
    )


def product_list_api(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    payload = fetch_products(query=query, category=category_slug) or {"items": [], "categories": []}
    return JsonResponse(payload)
