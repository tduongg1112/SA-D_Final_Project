from django.contrib import admin
from django.urls import include, path

from config import views as config_views

urlpatterns = [
    path("health", config_views.health, name="health"),
    path("admin/", admin.site.urls),
    path("api/cart/", include("apps.cart.api_urls")),
]

admin.site.site_header = "Cart Service Administration"
