from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Root URL → home page
    path('', home, name='home'),

    # Products app with namespace
    path('products/', include(('products.urls', 'products'), namespace='products')),

    # Users app (signup/profile views) with namespace
    path('accounts/', include(('users.urls', 'users'), namespace='users')),

    # Django's built-in auth system (login/logout/password management)
    path('accounts/', include('django.contrib.auth.urls')),

    # Shop app
    path("shop/", include(("shop.urls", "shop"), namespace="shop")),
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
