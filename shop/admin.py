import csv
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rangefilter.filters import NumericRangeFilter
from .models import Category, Product, Order, OrderItem


# -----------------------------
# Category Admin
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "product_count"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_per_page = 25

    def product_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span style="background: #e3f2fd; padding: 4px 8px; border-radius: 12px; font-weight: 600; color: #1976d2;">{}</span>',
            count
        )
    product_count.short_description = "Products"


# -----------------------------
# Product Admin
# -----------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
    "product_image_preview",
    "name",
    "brand",
    "category",
    "price",
    "discounted_price_display",
    "stock",              # added ✅
    "available",          # added ✅
    "stock_status",
    "availability_badge",
    "created",
]

    list_editable = ("stock", "available")
 
    list_filter = [
        "available", 
        "created", 
        "updated", 
        "category", 
        "brand",
        ("price", NumericRangeFilter),
        ("stock", NumericRangeFilter),
    ]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description", "model", "brand", "model_number"]
    readonly_fields = ["created", "updated", "product_image_preview"]
    list_per_page = 25
    date_hierarchy = 'created'

    fieldsets = (
        ("Product Information", {
            "fields": (
                "name", "slug", "category", "description", 
                "image", "product_image_preview"
            )
        }),
        ("Brand & Model Details", {
            "fields": ("brand", "model", "model_number"),
            "classes": ("collapse",)
        }),
        ("Pricing & Discounts", {
            "fields": (
                "price", "discount_amount", "discount_percentage", 
                "discount", "available", "stock"
            )
        }),
        ("Specifications", {
            "fields": ("weight", "dimensions", "warranty", "shipping"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created", "updated"),
            "classes": ("collapse",)
        }),
    )

    def product_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; border: 2px solid #e0e0e0;" />',
                obj.image.url
            )
        return format_html('<div style="width: 60px; height: 60px; background: #f5f5f5; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #999;">No Image</div>')
    product_image_preview.short_description = "Image"

    def discounted_price_display(self, obj):
        discounted = obj.get_discounted_price()
        if discounted < obj.price:
            savings = obj.price - discounted
            return format_html(
                '<div style="font-weight: 600; color: #d32f2f;">₹{:.2f}</div><div style="font-size: 11px; color: #4caf50;">Save ₹{:.2f}</div>',
                discounted, savings
            )
        return format_html('<span style="color: #666;">₹{:.2f}</span>', obj.price)
    discounted_price_display.short_description = "Final Price"

    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="background: #ffebee; color: #c62828; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">OUT OF STOCK</span>')
        elif obj.stock <= 5:
            return format_html('<span style="background: #fff3e0; color: #ef6c00; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">LOW STOCK ({})</span>', obj.stock)
        else:
            return format_html('<span style="background: #e8f5e8; color: #2e7d32; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">IN STOCK ({})</span>', obj.stock)
    stock_status.short_description = "Stock"

    def availability_badge(self, obj):
        if obj.available:
            return format_html('<span style="background: #4caf50; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ ACTIVE</span>')
        return format_html('<span style="background: #f44336; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">✗ INACTIVE</span>')
    availability_badge.short_description = "Status"


# -----------------------------
# Enhanced Order Item Inline
# -----------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_image", "product_details", "line_total", "product_stock_info"]
    fields = ["product_image", "product_details", "quantity", "price", "line_total", "product_stock_info"]
    
    def product_image(self, obj):
        if obj.product and obj.product.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.product.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f5f5f5; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #999;">No Image</div>')
    product_image.short_description = "Image"

    def product_details(self, obj):
        if obj.product:
            return format_html(
                '<div style="font-weight: 600; color: #1976d2; margin-bottom: 4px;">{}</div>'
                '<div style="font-size: 11px; color: #666;">SKU: {}</div>'
                '<div style="font-size: 11px; color: #666;">Brand: {}</div>',
                obj.product.name,
                f"GS-{obj.product.id:04d}",
                obj.product.brand or "N/A"
            )
        return "N/A"
    product_details.short_description = "Product Details"

    def line_total(self, obj):
        total = obj.get_cost()
        return format_html(
            '<div style="font-weight: 700; font-size: 14px; color: #2e7d32;">₹{:.2f}</div>',
            total
        )
    line_total.short_description = "Total"

    def product_stock_info(self, obj):
        if obj.product:
            if obj.product.stock >= obj.quantity:
                return format_html('<span style="color: #4caf50; font-size: 11px;">✓ Available</span>')
            else:
                return format_html('<span style="color: #f44336; font-size: 11px;">⚠ Low Stock</span>')
        return "N/A"
    product_stock_info.short_description = "Stock"


# -----------------------------
# Enhanced Order Admin
# -----------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "customer_info_display",
        "order_summary",
        "payment_info_display",
        "status_badge",
        "order_date",
        "quick_actions"
    ]
    
    list_filter = [
        "status",
        "payment_status", 
        "payment_method",
        "paid",
        ("created_at", admin.DateFieldListFilter),
        ("total_amount",  NumericRangeFilter),
        "country",
        "state"
    ]
    
    search_fields = [
        "id",
        "customer_name", 
        "customer_email", 
        "phone_number",
        "tracking_number",
        "razorpay_order_id",
        "payment_id"
    ]
    
    readonly_fields = [
        "created_at", 
        "updated_at", 
        "order_summary_detailed",
        "customer_details",
        "delivery_address_formatted",
        "payment_details",
        "order_timeline"
    ]
    
    inlines = [OrderItemInline]
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ("Order Information", {
            "fields": ("status", "tracking_number", "order_summary_detailed")
        }),
        ("Customer Information", {
            "fields": ("customer_details", "user")
        }),
        ("Delivery Details", {
            "fields": ("delivery_address_formatted", "delivery_latitude", "delivery_longitude")
        }),
        ("Payment Information", {
            "fields": ("payment_details", "paid", "notes")
        }),
        ("Order Timeline", {
            "fields": ("order_timeline",),
            "classes": ("wide",)
        }),
        ("Additional Information", {
            "fields": ("delivery_status",),
            "classes": ("collapse",)
        }),
    )

    # Custom display methods
    def order_number(self, obj):
        return format_html(
            '<div style="font-weight: 700; color: #1976d2; font-size: 14px;">#{}</div>'
            '<div style="font-size: 11px; color: #666;">{}</div>',
            obj.id,
            obj.created_at.strftime("%d %b, %Y")
        )
    order_number.short_description = "Order #"

    def customer_info_display(self, obj):
        return format_html(
            '<div style="font-weight: 600; margin-bottom: 4px;">{}</div>'
            '<div style="font-size: 11px; color: #666; margin-bottom: 2px;">📧 {}</div>'
            '<div style="font-size: 11px; color: #666;">📱 {}</div>',
            obj.customer_name,
            obj.customer_email,
            obj.phone_number or "N/A"
        )
    customer_info_display.short_description = "Customer"

    def order_summary(self, obj):
        item_count = obj.items.count()
        return format_html(
            '<div style="font-weight: 700; font-size: 16px; color: #2e7d32; margin-bottom: 4px;">₹{:.2f}</div>'
            '<div style="font-size: 11px; color: #666;">{} item{}</div>',
            obj.total_amount,
            item_count,
            "s" if item_count != 1 else ""
        )
    order_summary.short_description = "Order Value"

    def payment_info_display(self, obj):
        payment_status_colors = {
            'Pending': '#ff9800',
            'Paid': '#4caf50',
            'Failed': '#f44336'
        }
        
        status_color = payment_status_colors.get(obj.payment_status, '#666')
        
        return format_html(
            '<div style="margin-bottom: 4px;">'
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: 600;">{}</span>'
            '</div>'
            '<div style="font-size: 11px; color: #666;">Method: {}</div>'
            '<div style="font-size: 11px; color: #666;">Razorpay: {}</div>',
            status_color,
            obj.payment_status,
            obj.payment_method,
            obj.razorpay_order_id[:15] + "..." if obj.razorpay_order_id else "N/A"
        )
    payment_info_display.short_description = "Payment"

    def status_badge(self, obj):
        status_colors = {
            'PLACED': '#2196f3',
            'PACKED': '#ff9800', 
            'SHIPPED': '#9c27b0',
            'OUT_FOR_DELIVERY': '#ff5722',
            'DELIVERED': '#4caf50',
            'PAYMENT_FAILED': '#f44336',
            'CANCELLED': '#757575',
            'RETURNED': '#795548'
        }
        
        color = status_colors.get(obj.status, '#666')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 12px; border-radius: 16px; font-size: 11px; font-weight: 600; text-transform: uppercase;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def order_date(self, obj):
        return format_html(
            '<div style="font-weight: 600;">{}</div>'
            '<div style="font-size: 11px; color: #666;">{}</div>',
            obj.created_at.strftime("%d %b, %Y"),
            obj.created_at.strftime("%I:%M %p")
        )
    order_date.short_description = "Order Date"

    def quick_actions(self, obj):
        return format_html(
            '<div style="display: flex; gap: 4px; flex-direction: column;">'
            '<a href="{}" style="background: #1976d2; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; font-size: 10px; text-align: center;">📋 Details</a>'
            '<a href="{}" target="_blank" style="background: #388e3c; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; font-size: 10px; text-align: center;">🖨️ Print</a>'
            '</div>',
            reverse("admin:shop_order_details", args=[obj.id]),
            reverse("admin:shop_print_order", args=[obj.id])
        )
    quick_actions.short_description = "Actions"

    # Detailed readonly field methods
    def order_summary_detailed(self, obj):
        items = obj.items.all()
        estimated_delivery = obj.created_at + timedelta(days=3)
        
        summary_html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; text-align: center;">
                <div>
                    <div style="font-size: 24px; margin-bottom: 5px;">📋</div>
                    <div style="font-size: 14px; opacity: 0.9;">Order Number</div>
                    <div style="font-size: 18px; font-weight: 700;">#{obj.id}</div>
                </div>
                <div>
                    <div style="font-size: 24px; margin-bottom: 5px;">💰</div>
                    <div style="font-size: 14px; opacity: 0.9;">Total Amount</div>
                    <div style="font-size: 18px; font-weight: 700;">₹{obj.total_amount:.2f}</div>
                </div>
                <div>
                    <div style="font-size: 24px; margin-bottom: 5px;">📦</div>
                    <div style="font-size: 14px; opacity: 0.9;">Items</div>
                    <div style="font-size: 18px; font-weight: 700;">{items.count()}</div>
                </div>
                <div>
                    <div style="font-size: 24px; margin-bottom: 5px;">🚚</div>
                    <div style="font-size: 14px; opacity: 0.9;">Est. Delivery</div>
                    <div style="font-size: 16px; font-weight: 600;">{estimated_delivery.strftime('%d %b, %Y')}</div>
                </div>
            </div>
        </div>
        """
        return mark_safe(summary_html)
    order_summary_detailed.short_description = "Order Summary"

    def customer_details(self, obj):
        info_html = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007cba;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 20px; margin-right: 10px;">👤</span>
                <strong style="font-size: 16px; color: #2c3e50;">{obj.customer_name}</strong>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="font-weight: 600; color: #34495e;">📧 Email:</span> 
                <a href="mailto:{obj.customer_email}" style="color: #3498db;">{obj.customer_email}</a>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="font-weight: 600; color: #34495e;">📱 Phone:</span> 
                <a href="tel:{obj.phone_number}" style="color: #27ae60;">{obj.phone_number or 'Not provided'}</a>
            </div>
            {f'<div><span style="font-weight: 600; color: #34495e;">👤 User Account:</span> {obj.user.username}</div>' if obj.user else '<div style="color: #e74c3c;">👤 Guest Order</div>'}
        </div>
        """
        return mark_safe(info_html)
    customer_details.short_description = "Customer Information"

    def delivery_address_formatted(self, obj):
        address_parts = []
        if obj.address: address_parts.append(obj.address)
        if obj.city: address_parts.append(obj.city)
        if obj.state: address_parts.append(obj.state)
        if obj.postal_code: address_parts.append(obj.postal_code)
        if obj.country: address_parts.append(obj.country)

        full_address = ", ".join(address_parts) if address_parts else "No address provided"
        
        maps_link = ""
        if obj.delivery_latitude and obj.delivery_longitude:
            maps_url = f"https://www.google.com/maps?q={obj.delivery_latitude},{obj.delivery_longitude}"
            maps_link = f'<div style="margin-top: 10px;"><a href="{maps_url}" target="_blank" style="background: #4285f4; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">🗺️ View on Google Maps</a></div>'

        address_html = f"""
        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 20px; margin-right: 10px;">🏠</span>
                <strong style="font-size: 16px; color: #2c3e50;">Delivery Address</strong>
            </div>
            <div style="color: #2c3e50; line-height: 1.5;">{full_address}</div>
            {maps_link}
        </div>
        """
        return mark_safe(address_html)
    delivery_address_formatted.short_description = "Delivery Address"

    def payment_details(self, obj):
        payment_html = f"""
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 20px; margin-right: 10px;">💳</span>
                <strong style="font-size: 16px; color: #2c3e50;">Payment Information</strong>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <div style="font-weight: 600; color: #34495e;">Payment Method:</div>
                    <div style="margin-bottom: 10px;">{obj.payment_method}</div>
                    
                    <div style="font-weight: 600; color: #34495e;">Payment Status:</div>
                    <div style="margin-bottom: 10px;">
                        <span style="background: {'#4caf50' if obj.payment_status == 'Paid' else '#ff9800' if obj.payment_status == 'Pending' else '#f44336'}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{obj.payment_status}</span>
                    </div>
                </div>
                <div>
                    <div style="font-weight: 600; color: #34495e;">Razorpay Order ID:</div>
                    <div style="margin-bottom: 10px; font-family: monospace; font-size: 12px;">{obj.razorpay_order_id or 'N/A'}</div>
                    
                    <div style="font-weight: 600; color: #34495e;">Payment ID:</div>
                    <div style="font-family: monospace; font-size: 12px;">{obj.payment_id or 'N/A'}</div>
                </div>
            </div>
        </div>
        """
        return mark_safe(payment_html)
    payment_details.short_description = "Payment Details"

    def order_timeline(self, obj):
        timeline_html = f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #6c757d;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 20px; margin-right: 10px;">⏰</span>
                <strong style="font-size: 16px; color: #2c3e50;">Order Timeline</strong>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="text-align: center; padding: 10px; background: white; border-radius: 6px;">
                    <div style="font-weight: 600; color: #28a745;">Order Placed</div>
                    <div style="font-size: 12px; color: #666;">{obj.created_at.strftime('%d %b, %Y %I:%M %p')}</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 6px;">
                    <div style="font-weight: 600; color: #17a2b8;">Last Updated</div>
                    <div style="font-size: 12px; color: #666;">{obj.updated_at.strftime('%d %b, %Y %I:%M %p')}</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 6px;">
                    <div style="font-weight: 600; color: #6f42c1;">Current Status</div>
                    <div style="font-size: 12px; color: #666;">{obj.get_status_display()}</div>
                </div>
            </div>
        </div>
        """
        return mark_safe(timeline_html)
    order_timeline.short_description = "Timeline"

    # Custom URLs for additional functionality
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "order-details/<int:order_id>/",
                self.admin_site.admin_view(self.order_details_view),
                name="shop_order_details",
            ),
            path(
                "print-order/<int:order_id>/",
                self.admin_site.admin_view(self.print_order_view),
                name="shop_print_order",
            ),
            path(
                "export-orders/",
                self.admin_site.admin_view(self.export_orders_view),
                name="shop_export_orders",
            ),
        ]
        return custom_urls + urls

    def order_details_view(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        context = {
            "title": f"Order Details - #{order.id}",
            "order": order,
            "opts": self.model._meta,
            "has_change_permission": self.has_change_permission(request),
        }
        return render(request, "admin/shop/order_details.html", context)

    def print_order_view(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        context = {
            "order": order,
            "print_date": timezone.now(),
            "company_info": {
                "name": "Gadget Shop",
                "address": "123 Tech Street, Digital City, 560001",
                "phone": "+91 98765 43210",
                "email": "orders@gadgetshop.com",
                "website": "www.gadgetshop.com",
                "gst": "GST123456789",
            },
        }
        return render(request, "shop/print_order_details.html", context)

    def export_orders_view(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Order ID", "Customer Name", "Email", "Phone", "Status", 
            "Payment Status", "Total Amount", "Order Date", "Items Count",
            "Razorpay Order ID", "Payment ID"
        ])

        orders = Order.objects.all().order_by("-created_at")
        for order in orders:
            writer.writerow([
                order.id, order.customer_name, order.customer_email,
                order.phone_number or "N/A", order.get_status_display(),
                order.payment_status, f"₹{order.total_amount}",
                order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                order.items.count(), order.razorpay_order_id or "N/A",
                order.payment_id or "N/A"
            ])

        return response

    # Bulk actions
    actions = [
        "mark_as_packed", "mark_as_shipped", "mark_as_delivered", 
        "mark_payment_as_paid", "export_selected_orders"
    ]

    def mark_as_packed(self, request, queryset):
        updated = queryset.update(status="PACKED")
        self.message_user(request, f"{updated} orders marked as packed.")
    mark_as_packed.short_description = "Mark selected orders as packed"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status="SHIPPED")
        self.message_user(request, f"{updated} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status="DELIVERED")
        self.message_user(request, f"{updated} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def mark_payment_as_paid(self, request, queryset):
        updated = queryset.update(payment_status="Paid", paid=True)
        self.message_user(request, f"{updated} orders marked as paid.")
    mark_payment_as_paid.short_description = "Mark payment as paid"

    def export_selected_orders(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="selected_orders.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Order ID", "Customer Name", "Email", "Status", 
            "Total Amount", "Payment Status", "Order Date"
        ])

        for order in queryset:
            writer.writerow([
                order.id, order.customer_name, order.customer_email,
                order.get_status_display(), f"₹{order.total_amount}",
                order.payment_status, order.created_at.strftime("%Y-%m-%d")
            ])

        return response
    export_selected_orders.short_description = "Export selected orders to CSV"


# -----------------------------
# Admin Site Customization
# -----------------------------
admin.site.site_header = "🛍️ Gadget Shop Admin Dashboard"
admin.site.site_title = "Gadget Shop Admin"
admin.site.index_title = "Welcome to Gadget Shop Administration"

# Add custom CSS
admin.site.index_template = 'admin/custom_index.html'