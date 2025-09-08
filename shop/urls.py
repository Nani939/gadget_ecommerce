from django.urls import path
from . import views
from django.contrib import admin

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),

    # Products
    path("products/", views.product_list, name="product_list"),
    path("category/<slug:category_slug>/", views.product_list, name="product_list_by_category"),
    path("product/<int:id>/<slug:slug>/", views.product_detail, name="product_detail"),

    # Cart
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/count/", views.cart_count, name="cart_count"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:product_id>/", views.update_quantity, name="update_quantity"),

    # Buy now
    path("buy/<int:product_id>/", views.buy_now, name="buy_now"),

    # Checkout & Orders
    path("checkout/", views.checkout, name="checkout"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("track/<int:order_id>/", views.track_order, name="track_order"),
    
    # Print and delivery management
    path("orders/", views.orders_list, name="orders"),
    path("order/print/<int:order_id>/", views.print_order_details, name="print_order_details"),
    path("order/delivery-slip/<int:order_id>/", views.delivery_slip, name="delivery_slip"),
    
    # Admin download URLs (for admin interface)
    path("admin/download-addresses/", views.download_addresses_admin, name="download_addresses_admin"),
    path("admin/download-single-address/<int:order_id>/", views.download_single_address_admin, name="download_single_address_admin"),
    
    # Unique features
    path("wishlist/", views.wishlist, name="wishlist"),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("compare/", views.compare_products, name="compare_products"),
    path("compare/add/<int:product_id>/", views.add_to_compare, name="add_to_compare"),
    path("quick-order/", views.quick_order, name="quick_order"),
    path("bulk-order/", views.bulk_order, name="bulk_order"),

    # FIXED section
    path("payment/success/", views.payment_success, name="payment_success"),  # ✅ Keep only this
    # ❌ REMOVE: path("order-success/", views.order_success, name="order_success"),
    # ❌ REMOVE duplicate: path("product/<int:pk>/", views.product_detail, name="product_detail"),
]
