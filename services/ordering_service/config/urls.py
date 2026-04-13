from django.contrib import admin
from django.urls import include, path

from config import views as config_views

urlpatterns = [
    path("health", config_views.health, name="health"),
    path("admin/", admin.site.urls),
    path("api/orders/", include("apps.ordering.api_urls")),
]

admin.site.site_header = "Ordering Service Administration"
