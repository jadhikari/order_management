from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Restaurant, RestaurantProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'role', 'restaurant', 'is_active', 'is_staff', 'created_at', 'updated_at']
    list_filter = ['role', 'restaurant', 'is_active', 'is_staff']
    search_fields = ['email']
    ordering = ['email']

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'restaurant')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'restaurant', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return qs
        if getattr(request.user, 'restaurant', None):
            return qs.filter(restaurant=request.user.restaurant)
        return qs.none()


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'unique_code', 'subscription_active', 'created_at', 'updated_at']
    readonly_fields = ['unique_code', 'created_at', 'updated_at']


@admin.register(RestaurantProfile)
class RestaurantProfileAdmin(admin.ModelAdmin):
    """
    Admin for RestaurantProfile.
    """
    list_display = ['restaurant', 'phone_number', 'address', 'website']
    search_fields = ['restaurant__name', 'phone_number']


