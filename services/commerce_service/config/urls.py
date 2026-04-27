from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from config import views as config_views

urlpatterns = [
    path("health", config_views.health, name="health"),
    path("api/ai/chat/", config_views.ai_chat, name="ai_chat"),
    path("admin/", admin.site.urls),
    path("", include("apps.storefront.urls")),
    path("products/", include("apps.catalog.urls")),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.ordering.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("api/products/", include("apps.catalog.api_urls")),
    path("api/catalog/", include("apps.catalog.api_urls")),
    path("api/cart/", include("apps.cart.api_urls")),
    path("api/orders/", include("apps.ordering.api_urls")),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

admin.site.site_header = "NovaMarket Administration"
admin.site.site_title = "NovaMarket Admin"
admin.site.index_title = "System administration"
