from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Product listings
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart functionality
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Checkout & order
    path('checkout/', views.checkout, name='checkout'),
    path('order/create/', views.order_create, name='order_create'),
]
from django.urls import path
from . import views

app_name = 'shop'  # <-- This defines the namespace

urlpatterns = [
     path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.home, name='home'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),

    # other shop URLs...
]
