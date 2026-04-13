from django.urls import path

from apps.ordering import views

urlpatterns = [
    path("", views.orders_api, name="api-orders"),
]
