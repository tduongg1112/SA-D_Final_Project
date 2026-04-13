from django.urls import path

from apps.catalog import views

urlpatterns = [
    path("", views.product_list_api, name="api-product-list-root"),
    path("products/", views.product_list_api, name="api-product-list"),
]
