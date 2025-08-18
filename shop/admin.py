from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "price", "available", "created", "updated"]
    list_filter = ["available", "created", "updated", "category"]
    list_editable = ["price", "available"]
    prepopulated_fields = {"slug": ("name",)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_name", "customer_email", "created_at", "paid"]
    list_filter = ["paid", "created_at"]
    inlines = [OrderItemInline]
