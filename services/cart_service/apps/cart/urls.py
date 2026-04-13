from django.urls import path

from apps.cart import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("add/<int:product_id>/", views.add_to_cart, name="add"),
    path("items/<int:item_id>/update/", views.update_item, name="update-item"),
    path("items/<int:item_id>/remove/", views.remove_item, name="remove-item"),
]
