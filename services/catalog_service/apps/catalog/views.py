from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.catalog.models import Category, Product


def product_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    products = Product.objects.filter(status=Product.Status.ACTIVE).select_related("category")
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(short_description__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(
        request,
        "pages/catalog/list.html",
        {
            "products": products,
            "categories": Category.objects.all(),
            "active_category": category_slug,
            "query": query,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        status=Product.Status.ACTIVE,
    )
    related_products = Product.objects.filter(
        category=product.category,
        status=Product.Status.ACTIVE,
    ).exclude(pk=product.pk)[:3]
    return render(
        request,
        "pages/catalog/detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )


def product_list_api(request):
    products = Product.objects.filter(status=Product.Status.ACTIVE).select_related("category")
    payload = [
        {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "category": product.category.name,
            "brand": product.brand,
            "price": str(product.price),
            "stock_quantity": product.stock_quantity,
            "featured": product.featured,
        }
        for product in products
    ]
    return JsonResponse({"items": payload})
