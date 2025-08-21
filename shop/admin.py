from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "price", "stock", "available", "created", "updated"]
    list_filter = ["available", "created", "updated", "category"]
    list_editable = ["price", "stock", "available"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name', 'description']
    readonly_fields = ['created', 'updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'available')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]
    readonly_fields = ['get_cost']
    extra = 0
    
    def get_cost(self, obj):
        if obj.id:
            return f"₹{obj.get_cost():.2f}"
        return "₹0.00"
    get_cost.short_description = "Total Cost"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id", "customer_name", "customer_email", "phone_number", 
        "status", "total_amount", "payment_method", "created_at", "paid"
    ]
    list_filter = ["paid", "status", "payment_method", "created_at"]
    search_fields = ["customer_name", "customer_email", "tracking_number"]
    readonly_fields = [
        'created_at', 'updated_at', 'get_total_cost', 'get_customer_info',
        'get_delivery_address', 'get_order_items'
    ]
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'status', 'tracking_number', 'created_at', 'updated_at')
        }),
        ('Customer Details', {
            'fields': ('get_customer_info', 'user')
        }),
        ('Delivery Address', {
            'fields': ('get_delivery_address', 'delivery_latitude', 'delivery_longitude')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'total_amount', 'get_total_cost', 'paid')
        }),
        ('Order Items', {
            'fields': ('get_order_items',),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'delivery_status'),
            'classes': ('collapse',)
        }),
    )
    
    def get_customer_info(self, obj):
        info = f"""
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <strong>Name:</strong> {obj.customer_name}<br>
            <strong>Email:</strong> <a href="mailto:{obj.customer_email}">{obj.customer_email}</a><br>
            <strong>Phone:</strong> {obj.phone_number or 'Not provided'}
        </div>
        """
        return mark_safe(info)
    get_customer_info.short_description = "Customer Information"
    
    def get_delivery_address(self, obj):
        address_parts = []
        if obj.address:
            address_parts.append(obj.address)
        if obj.city:
            address_parts.append(obj.city)
        if obj.state:
            address_parts.append(obj.state)
        if obj.postal_code:
            address_parts.append(obj.postal_code)
        if obj.country:
            address_parts.append(obj.country)
        
        full_address = ", ".join(address_parts) if address_parts else "No address provided"
        
        address_html = f"""
        <div style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <strong>Delivery Address:</strong><br>
            {full_address}
        </div>
        """
        return mark_safe(address_html)
    get_delivery_address.short_description = "Delivery Address"
    
    def get_order_items(self, obj):
        items = obj.items.all()
        if not items:
            return "No items"
        
        items_html = """
        <div style="background: #fff3e0; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <strong>Order Items:</strong><br>
            <table style="width: 100%; margin-top: 10px;">
                <tr style="background: #f5f5f5;">
                    <th style="padding: 5px; text-align: left;">Product</th>
                    <th style="padding: 5px; text-align: center;">Quantity</th>
                    <th style="padding: 5px; text-align: right;">Price</th>
                    <th style="padding: 5px; text-align: right;">Total</th>
                </tr>
        """
        
        for item in items:
            items_html += f"""
                <tr>
                    <td style="padding: 5px;">{item.product.name}</td>
                    <td style="padding: 5px; text-align: center;">{item.quantity}</td>
                    <td style="padding: 5px; text-align: right;">₹{item.price:.2f}</td>
                    <td style="padding: 5px; text-align: right;">₹{item.get_cost():.2f}</td>
                </tr>
            """
        
        items_html += f"""
            </table>
            <div style="margin-top: 10px; text-align: right; font-weight: bold;">
                <strong>Total: ₹{obj.get_total_cost():.2f}</strong>
            </div>
        </div>
        """
        return mark_safe(items_html)
    get_order_items.short_description = "Order Items"
    
    def get_total_cost(self, obj):
        return f"₹{obj.get_total_cost():.2f}"
    get_total_cost.short_description = "Calculated Total"
    
    actions = ['mark_as_packed', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_packed(self, request, queryset):
        updated = queryset.update(status='PACKED')
        self.message_user(request, f'{updated} orders marked as packed.')
    mark_as_packed.short_description = "Mark selected orders as packed"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='SHIPPED')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='DELIVERED')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"