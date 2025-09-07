from django import template
from django.utils.safestring import mark_safe
from datetime import timedelta
from django.db import models

register = template.Library()

@register.filter
def add_days(date, days):
    """Add days to a date"""
    try:
        return date + timedelta(days=int(days))
    except (ValueError, TypeError):
        return date

@register.simple_tag
def get_order_stats():
    """Get order statistics for admin dashboard"""
    from shop.models import Order
    from django.db.models import Sum, Count, Q
    
    stats = Order.objects.aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('total_amount'),
        pending_orders=Count('id', filter=Q(status='PLACED')),
        shipped_orders=Count('id', filter=Q(status='SHIPPED')),
    )
    
    return stats

@register.inclusion_tag('admin/shop/order_stats.html')
def show_order_stats():
    """Display order statistics"""
    from shop.models import Order
    from django.db.models import Sum, Count, Q
    
    stats = {
        'total_orders': Order.objects.count(),
        'total_revenue': Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'pending_orders': Order.objects.filter(status='PLACED').count(),
        'shipped_orders': Order.objects.filter(status='SHIPPED').count(),
        'delivered_orders': Order.objects.filter(status='DELIVERED').count(),
    }
    
    return {'stats': stats}