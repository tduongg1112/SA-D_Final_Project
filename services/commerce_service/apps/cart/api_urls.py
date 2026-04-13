from django.urls import path

from apps.cart import views

urlpatterns = [
    path("", views.cart_api, name="api-cart"),
]
