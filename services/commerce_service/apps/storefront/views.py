from django.shortcuts import render

from config.service_clients import fetch_products


def home(request):
    payload = fetch_products() or {"items": [], "categories": []}
    products = payload["items"]
    featured_products = [product for product in products if product["featured"]][:4]
    categories = payload["categories"][:6]
    latest_products = products[:8]
    return render(
        request,
        "pages/home.html",
        {
            "featured_products": featured_products,
            "categories": categories,
            "latest_products": latest_products,
        },
    )
