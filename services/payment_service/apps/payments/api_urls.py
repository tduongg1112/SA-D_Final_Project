from django.urls import path

from apps.payments import views

urlpatterns = [
    path("", views.payments_api, name="api-payments"),
    path("order/<int:order_id>/", views.payment_detail_api, name="api-payment-detail"),
]
