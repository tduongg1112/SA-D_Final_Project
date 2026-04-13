from django.urls import path

from apps.shipping import views

urlpatterns = [
    path("", views.shipments_api, name="api-shipments"),
    path("order/<int:order_id>/", views.shipment_detail_api, name="api-shipment-detail"),
]
