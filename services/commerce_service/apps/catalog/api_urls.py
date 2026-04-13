from django.urls import path

from apps.catalog import views

urlpatterns = [
    path("products/", views.product_list_api, name="api-product-list"),
]
