from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout/password views
    path('accounts/', include('users.urls')),                # signup + profile
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('products/', include('products.urls')),
    path('users/', include('users.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # public site
    path('', include('shop.urls')),           # home, cart, checkout
    path('products/', include('products.urls')),  # product list + detail
    path('accounts/', include('users.urls')),  
     
]
from django.shortcuts import redirect

def profile_redirect(request):
    # Redirect to home or user dashboard
    return redirect('shop:home')  # or any other named url

urlpatterns = [
    # ... your other patterns
    path('profile/', profile_redirect, name='profile'),
]
from django.urls import path, include
from django.contrib import admin
from shop import views as shop_views  # Assuming you have a home view here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', shop_views.home, name='home'),  # Root path mapped to home view
    path('accounts/', include('users.urls')),  # Your users app URLs
    path('products/', include('products.urls')),  # Your products app URLs
    # other paths...
]
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls', namespace='shop')),  # <-- Add namespace here
    path('accounts/', include('users.urls')),
    path('products/', include('products.urls')),
    # other paths...
]
