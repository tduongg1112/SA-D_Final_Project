from django.urls import path

from apps.ordering import views

app_name = "ordering"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("<int:order_id>/success/", views.order_success, name="success"),
]
