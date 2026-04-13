from django.urls import path

from apps.cart import views

urlpatterns = [
    path("", views.cart_api, name="api-cart"),
    path("clear/", views.clear_cart_api, name="api-cart-clear"),
    path("items/", views.add_item_api, name="api-cart-add-item"),
    path("items/<int:item_id>/", views.update_item_api, name="api-cart-update-item"),
    path("items/<int:item_id>/remove/", views.remove_item_api, name="api-cart-remove-item"),
]
