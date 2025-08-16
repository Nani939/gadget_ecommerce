from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
]
# shop/urls.py or wherever your product views are

from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),  # ✅ name='product_list'
]
from django.urls import path
from . import views

app_name = 'products'  # ✅ Optional but good practice when using namespacing

urlpatterns = [
    path('', views.product_list, name='product_list'), 
     path('<int:pk>/', views.product_detail, name='product_detail'),  # ✅ name must match
]
