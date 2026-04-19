from django.urls import path

from apps.catalog import views

urlpatterns = [
    path("", views.product_list_api, name="api-product-list-root"),
    path("products/", views.product_list_api, name="api-product-list"),
    path("id/<int:product_id>/", views.product_detail_by_id_api, name="api-product-detail-by-id"),
    path("stock/reserve/", views.reserve_stock_api, name="api-product-stock-reserve"),
    path("<slug:slug>/", views.product_detail_api, name="api-product-detail"),
]
