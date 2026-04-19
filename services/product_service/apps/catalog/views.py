import json

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from apps.catalog.models import Category, Product


def serialize_category(category):
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
    }


def serialize_product(product):
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "absolute_url": f"/products/{product.slug}/",
        "category": serialize_category(product.category),
        "brand": product.brand,
        "short_description": product.short_description,
        "description": product.description,
        "price": str(product.price),
        "stock_quantity": product.stock_quantity,
        "featured": product.featured,
        "status": product.status,
        "status_label": product.get_status_display(),
        "accent_color": product.accent_color,
        "is_in_stock": product.is_in_stock,
    }


def build_product_queryset(query="", category_slug=""):
    products = Product.objects.filter(status=Product.Status.ACTIVE).select_related("category")
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(short_description__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return products


def product_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    products = build_product_queryset(query=query, category_slug=category_slug)
    categories = Category.objects.filter(products__status=Product.Status.ACTIVE).distinct()
    return render(
        request,
        "pages/catalog/list.html",
        {
            "products": products,
            "categories": categories,
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
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    products = build_product_queryset(query=query, category_slug=category_slug)
    categories = Category.objects.filter(products__status=Product.Status.ACTIVE).distinct()
    return JsonResponse(
        {
            "items": [serialize_product(product) for product in products],
            "categories": [serialize_category(category) for category in categories],
        }
    )


def product_detail_api(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        status=Product.Status.ACTIVE,
    )
    related_products = Product.objects.filter(
        category=product.category,
        status=Product.Status.ACTIVE,
    ).exclude(pk=product.pk)[:3]
    return JsonResponse(
        {
            "product": serialize_product(product),
            "related_products": [serialize_product(item) for item in related_products],
        }
    )


def product_detail_by_id_api(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=product_id,
        status=Product.Status.ACTIVE,
    )
    return JsonResponse(serialize_product(product))


@csrf_exempt
def reserve_stock_api(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    items = payload.get("items") or []
    normalized_items = []
    for item in items:
        product_id = item.get("product_id")
        quantity = int(item.get("quantity", 0))
        if not product_id or quantity < 1:
            return JsonResponse({"detail": "Each stock item must include product_id and quantity."}, status=400)
        normalized_items.append({"product_id": int(product_id), "quantity": quantity})

    if not normalized_items:
        return JsonResponse({"detail": "No stock items were provided."}, status=400)

    reserved_items = []
    with transaction.atomic():
        products = {
            product.id: product
            for product in Product.objects.select_for_update().select_related("category").filter(
                id__in=[item["product_id"] for item in normalized_items],
                status=Product.Status.ACTIVE,
            )
        }
        for item in normalized_items:
            product = products.get(item["product_id"])
            if product is None:
                return JsonResponse(
                    {"detail": f"Product {item['product_id']} is unavailable."},
                    status=404,
                )
            if product.stock_quantity < item["quantity"]:
                return JsonResponse(
                    {
                        "detail": f"Insufficient stock for product {product.id}.",
                        "product_id": product.id,
                        "available_quantity": product.stock_quantity,
                    },
                    status=409,
                )

        for item in normalized_items:
            product = products[item["product_id"]]
            product.stock_quantity -= item["quantity"]
            product.save(update_fields=["stock_quantity"])
            reserved_items.append(
                {
                    "product_id": product.id,
                    "remaining_stock": product.stock_quantity,
                }
            )

    return JsonResponse({"items": reserved_items}, status=200)
