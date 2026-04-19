from django.contrib import admin
from django.urls import include, path

from config import views as config_views

urlpatterns = [
    path("health", config_views.health, name="health"),
    path("admin/", admin.site.urls),
    path("api/products/", include("apps.catalog.api_urls")),
    path("api/catalog/", include("apps.catalog.api_urls")),
]

admin.site.site_header = "Product Service Administration"
