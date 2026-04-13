from django.urls import path

from apps.ordering import views

urlpatterns = [
    path("checkout/", views.checkout_api, name="api-order-checkout"),
    path("", views.orders_api, name="api-orders"),
    path("<int:order_id>/", views.order_detail_api, name="api-order-detail"),
]
