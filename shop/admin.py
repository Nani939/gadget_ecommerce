import csv
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
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
    readonly_fields = ['get_cost', 'product_image']
    extra = 0
    
    def get_cost(self, obj):
        if obj.id:
            return f"₹{obj.get_cost():.2f}"
        return "₹0.00"
    get_cost.short_description = "Total Cost"
    
    def product_image(self, obj):
        if obj.product and obj.product.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain;" />',
                obj.product.image.url
            )
        return "No Image"
    product_image.short_description = "Image"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id", "customer_name", "customer_email", "phone_number", 
        "status", "total_amount", "payment_method", "created_at", "paid",
        "view_order_details", "print_order_details", "download_address"
    ]
    list_filter = ["paid", "status", "payment_method", "created_at", "country", "state"]
    search_fields = ["customer_name", "customer_email", "tracking_number", "phone_number"]
    readonly_fields = [
        'created_at', 'updated_at', 'get_total_cost', 'get_customer_info',
        'get_delivery_address', 'get_order_items', 'get_order_summary'
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
        ('Order Summary', {
            'fields': ('get_order_summary',),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'delivery_status'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('order-details/<int:order_id>/', 
                 self.admin_site.admin_view(self.order_details_view), 
                 name='shop_order_details'),
            path('print-order/<int:order_id>/', 
                 self.admin_site.admin_view(self.print_order_view),  # ✅ admin_view protects staff-only
                 name='shop_print_order'),
            path('download-addresses/', 
                 self.admin_site.admin_view(self.download_addresses_view), 
                 name='shop_download_addresses'),
            path('download-single-address/<int:order_id>/', 
                 self.admin_site.admin_view(self.download_single_address_view), 
                 name='shop_download_single_address'),
        ]
        return custom_urls + urls
    
    def view_order_details(self, obj):
        url = reverse('admin:shop_order_details', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" style="background: #417690; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">📋 View Details</a>',
            url
        )
    view_order_details.short_description = "Order Details"
    
    def print_order_details(self, obj):
        url = reverse('admin:shop_print_order', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" class="button" style="background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">🖨️ Print</a>',
            url
        )
    print_order_details.short_description = "Print Order"
    
    def download_address(self, obj):
        url = reverse('admin:shop_download_single_address', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" style="background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">📥 Address</a>',
            url
        )
    download_address.short_description = "Download Address"
    
    def order_details_view(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        context = {
            'title': f'Order Details - #{order.id}',
            'order': order,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'admin/shop/order_details.html', context)
    
    def print_order_view(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        context = {
            'order': order,
            'print_date': __import__('datetime').datetime.now(),
            'company_info': {
                'name': 'Gadget Shop',
                'address': '123 Tech Street, Digital City, 560001',
                'phone': '+91 98765 43210',
                'email': 'orders@gadgetshop.com',
                'website': 'www.gadgetshop.com',
                'gst': 'GST123456789'
            }
        }
        return render(request, 'shop/print_order_details.html', context)
    
    
    def download_addresses_view(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="delivery_addresses.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Customer Name', 'Phone', 'Email', 'Address', 
            'City', 'State', 'Postal Code', 'Country', 'Order Date', 
            'Status', 'Total Amount', 'Payment Method', 'Latitude', 'Longitude'
        ])
        
        orders = Order.objects.all().order_by('-created_at')
        for order in orders:
            writer.writerow([
                order.id,
                order.customer_name,
                order.phone_number or 'N/A',
                order.customer_email,
                order.address or 'N/A',
                order.city or 'N/A',
                order.state or 'N/A',
                order.postal_code or 'N/A',
                order.country,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.get_status_display(),
                f'₹{order.total_amount}',
                order.payment_method,
                order.delivery_latitude or 'N/A',
                order.delivery_longitude or 'N/A',
            ])
        
        return response
    
    def download_single_address_view(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="order_{order.id}_address.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Customer Name', 'Phone', 'Email', 'Address', 
            'City', 'State', 'Postal Code', 'Country', 'Order Date', 
            'Status', 'Total Amount', 'Payment Method', 'Items', 'Latitude', 'Longitude'
        ])
        
        items_list = ', '.join([f"{item.product.name} (Qty: {item.quantity})" for item in order.items.all()])
        
        writer.writerow([
            order.id,
            order.customer_name,
            order.phone_number or 'N/A',
            order.customer_email,
            order.address or 'N/A',
            order.city or 'N/A',
            order.state or 'N/A',
            order.postal_code or 'N/A',
            order.country,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.get_status_display(),
            f'₹{order.total_amount}',
            order.payment_method,
            items_list,
            order.delivery_latitude or 'N/A',
            order.delivery_longitude or 'N/A',
        ])
        
        return response
    
    def get_customer_info(self, obj):
        info = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 5px 0; border-left: 4px solid #007cba;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 20px; margin-right: 10px;">👤</span>
                <strong style="font-size: 16px; color: #2c3e50;">{obj.customer_name}</strong>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="font-weight: 600; color: #34495e;">📧 Email:</span> 
                <a href="mailto:{obj.customer_email}" style="color: #3498db; text-decoration: none;">{obj.customer_email}</a>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="font-weight: 600; color: #34495e;">📱 Phone:</span> 
                <a href="tel:{obj.phone_number}" style="color: #27ae60; text-decoration: none;">{obj.phone_number or 'Not provided'}</a>
            </div>
            {f'<div><span style="font-weight: 600; color: #34495e;">👤 User Account:</span> {obj.user.username}</div>' if obj.user else '<div style="color: #e74c3c;">👤 Guest Order</div>'}
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
        
        # Google Maps link if coordinates are available
        maps_link = ""
        if obj.delivery_latitude and obj.delivery_longitude:
            maps_url = f"https://www.google.com/maps?q={obj.delivery_latitude},{obj.delivery_longitude}"
            maps_link = f'<div style="margin-top: 10px;"><a href="{maps_url}" target="_blank" style="background: #4285f4; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">🗺️ View on Google Maps</a></div>'
        
        address_html = f"""
        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 5px 0; border-left: 4px solid #28a745;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 20px; margin-right: 10px;">🏠</span>
                <strong style="font-size: 16px; color: #2c3e50;">Delivery Address</strong>
            </div>
            <div style="color: #2c3e50; line-height: 1.5;">
                {full_address}
            </div>
            {maps_link}
        </div>
        """
        return mark_safe(address_html)
    get_delivery_address.short_description = "Delivery Address"
    
    def get_order_items(self, obj):
        items = obj.items.all()
        if not items:
            return "No items"
        
        items_html = """
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 5px 0; border-left: 4px solid #ffc107;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 20px; margin-right: 10px;">📦</span>
                <strong style="font-size: 16px; color: #2c3e50;">Order Items</strong>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                        <th style="padding: 10px; text-align: left; font-weight: 600;">Image</th>
                        <th style="padding: 10px; text-align: left; font-weight: 600;">Product</th>
                        <th style="padding: 10px; text-align: center; font-weight: 600;">Quantity</th>
                        <th style="padding: 10px; text-align: right; font-weight: 600;">Unit Price</th>
                        <th style="padding: 10px; text-align: right; font-weight: 600;">Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in items:
            image_html = ""
            if item.product.image:
                image_html = f'<img src="{item.product.image.url}" style="width: 40px; height: 40px; object-fit: contain; border-radius: 4px;" />'
            else:
                image_html = '<div style="width: 40px; height: 40px; background: #f8f9fa; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #6c757d;">No Image</div>'
            
            items_html += f"""
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 10px;">{image_html}</td>
                    <td style="padding: 10px; font-weight: 500;">{item.product.name}</td>
                    <td style="padding: 10px; text-align: center;">
                        <span style="background: #e9ecef; padding: 4px 8px; border-radius: 12px; font-weight: 600;">{item.quantity}</span>
                    </td>
                    <td style="padding: 10px; text-align: right;">₹{item.price:.2f}</td>
                    <td style="padding: 10px; text-align: right; font-weight: 600; color: #28a745;">₹{item.get_cost():.2f}</td>
                </tr>
            """
        
        items_html += f"""
                </tbody>
            </table>
            <div style="margin-top: 15px; text-align: right; padding-top: 10px; border-top: 2px solid #28a745;">
                <span style="font-size: 18px; font-weight: 700; color: #28a745;">
                    Grand Total: ₹{obj.get_total_cost():.2f}
                </span>
            </div>
        </div>
        """
        return mark_safe(items_html)
    get_order_items.short_description = "Order Items"
    
    def get_order_summary(self, obj):
        estimated_delivery = obj.created_at + __import__('datetime').timedelta(days=3)
        
        summary_html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">📋</div>
                    <div style="font-size: 14px; opacity: 0.9;">Order Number</div>
                    <div style="font-size: 18px; font-weight: 700;">#{obj.id}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">📅</div>
                    <div style="font-size: 14px; opacity: 0.9;">Order Date</div>
                    <div style="font-size: 16px; font-weight: 600;">{obj.created_at.strftime('%B %d, %Y')}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">💰</div>
                    <div style="font-size: 14px; opacity: 0.9;">Total Amount</div>
                    <div style="font-size: 18px; font-weight: 700;">₹{obj.total_amount:.2f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">💳</div>
                    <div style="font-size: 14px; opacity: 0.9;">Payment Method</div>
                    <div style="font-size: 16px; font-weight: 600;">{obj.payment_method}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">📦</div>
                    <div style="font-size: 14px; opacity: 0.9;">Status</div>
                    <div style="font-size: 16px; font-weight: 600;">{obj.get_status_display()}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">🚚</div>
                    <div style="font-size: 14px; opacity: 0.9;">Est. Delivery</div>
                    <div style="font-size: 16px; font-weight: 600;">{estimated_delivery.strftime('%B %d, %Y')}</div>
                </div>
            </div>
        </div>
        """
        return mark_safe(summary_html)
    get_order_summary.short_description = "Order Summary"
    
    def get_total_cost(self, obj):
        return f"₹{obj.get_total_cost():.2f}"
    get_total_cost.short_description = "Calculated Total"
    
    actions = ['mark_as_packed', 'mark_as_shipped', 'mark_as_delivered', 'export_addresses']
    
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
    
    def export_addresses(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="selected_orders_addresses.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Customer Name', 'Phone', 'Email', 'Address', 
            'City', 'State', 'Postal Code', 'Country', 'Order Date', 
            'Status', 'Total Amount', 'Payment Method', 'Items', 'Latitude', 'Longitude'
        ])
        
        for order in queryset:
            items_list = ', '.join([f"{item.product.name} (Qty: {item.quantity})" for item in order.items.all()])
            writer.writerow([
                order.id,
                order.customer_name,
                order.phone_number or 'N/A',
                order.customer_email,
                order.address or 'N/A',
                order.city or 'N/A',
                order.state or 'N/A',
                order.postal_code or 'N/A',
                order.country,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.get_status_display(),
                f'₹{order.total_amount}',
                order.payment_method,
                items_list,
                order.delivery_latitude or 'N/A',
                order.delivery_longitude or 'N/A',
            ])
        
        return response
    export_addresses.short_description = "Export selected addresses to CSV"

# Add custom admin site configuration
admin.site.site_header = "Gadget Shop Admin Dashboard"
admin.site.site_title = "Gadget Shop Admin"
admin.site.index_title = "Welcome to Gadget Shop Administration"