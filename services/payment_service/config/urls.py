from django.contrib import admin
from django.urls import include, path

from config import views as config_views

urlpatterns = [
    path("health", config_views.health, name="health"),
    path("admin/", admin.site.urls),
    path("api/payments/", include("apps.payments.api_urls")),
]

admin.site.site_header = "Payment Service Administration"
