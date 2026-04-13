from django.contrib import admin

from apps.catalog.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "stock_quantity", "featured", "status")
    list_filter = ("featured", "status", "category")
    search_fields = ("name", "brand", "short_description")
    prepopulated_fields = {"slug": ("name",)}

# Register your models here.
