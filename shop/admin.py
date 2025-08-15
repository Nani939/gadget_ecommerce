from django.contrib import admin
from .models import Category, Product, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}  # Optional: allows slug to auto-fill in admin


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "available")
    list_filter = ("category", "available")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "customer_name", "quantity", "status", "order_date")
    list_filter = ("status", "order_date")
    search_fields = ("customer_name", "customer_email")
    actions = ["mark_as_confirmed"]

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_as_confirmed(self, request, queryset):
        updated_count = queryset.update(status="confirmed")
        self.message_user(request, f"{updated_count} orders marked as confirmed.")
