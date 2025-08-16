from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Product URLs
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('products/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Buy now shortcut
    path('buy/<int:product_id>/', views.buy_now, name='buy_now'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
]
