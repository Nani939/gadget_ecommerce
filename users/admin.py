from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address, UserProfile

# Register CustomUser with enhanced admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'is_admin')}),
    )

# Register Address with correct field names
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'address_line1', 'city', 'zip_code', 'is_default')
    list_filter = ('is_default', 'country', 'state')
    search_fields = ('user__username', 'full_name', 'phone_number', 'city')
    list_editable = ('is_default',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'phone_number')
        }),
        ('Address Details', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code', 'country')
        }),
        ('Settings', {
            'fields': ('is_default',)
        }),
    )

# Register UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'postal_code')
    search_fields = ('user__username', 'city')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'postal_code')
        }),
    )