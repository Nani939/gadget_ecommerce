from django.urls import path
from . import views

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
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", views.update_quantity, name="update_quantity"),

    # Buy now
    path("buy/<int:product_id>/", views.buy_now, name="buy_now"),

    # Checkout & Orders
    path("checkout/", views.checkout, name="checkout"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("track/<int:order_id>/", views.track_order, name="track_order"),

]
