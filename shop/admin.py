from django.contrib import admin
from .models import Category, Product, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}  # Automatically fills slug from name

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available', 'created', 'updated')
    list_filter = ('available', 'category', 'created', 'updated')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}  # Automatically fills slug from name

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'product', 'quantity', 'status', 'order_date')
    list_filter = ('status', 'order_date')
    search_fields = ('customer_name', 'customer_email')
