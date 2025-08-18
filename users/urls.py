from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'  # This enables namespacing for the users app URLs

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('signup/', views.signup_view, name='signup'),  # Your custom signup view
    path('address/add/', views.add_address, name='add_address'),
    path('profile/', views.profile_view, name='profile'),  # Profile view URL
]
