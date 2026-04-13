from django.shortcuts import render

from apps.catalog.models import Category, Product


def home(request):
    featured_products = Product.objects.filter(
        featured=True,
        status=Product.Status.ACTIVE,
    ).select_related("category")[:4]
    categories = Category.objects.all()[:4]
    latest_products = Product.objects.filter(status=Product.Status.ACTIVE).select_related("category")[:6]
    return render(
        request,
        "pages/home.html",
        {
            "featured_products": featured_products,
            "categories": categories,
            "latest_products": latest_products,
        },
    )
