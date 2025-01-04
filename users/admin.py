from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser, Restaurant, Profile


# Custom User Form
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'restaurant' in self.fields:
            self.fields['restaurant'].queryset = Restaurant.objects.filter(subscription_active=True)


# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    list_display = ['email', 'role', 'get_restaurant_name', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password', 'role', 'restaurant')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'restaurant'),
        }),
    )

    def get_queryset(self, request):
        """
        Restrict the queryset based on user role:
        - Super Admin: Access all users.
        - Other roles: Access only users in their restaurant.
        """
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        elif request.user.restaurant:
            return qs.filter(restaurant=request.user.restaurant)
        return qs.none()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name if obj.restaurant else "N/A"
    get_restaurant_name.short_description = "Restaurant"


# Restaurant Admin
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'unique_code', 'subscription_active', 'subscription_date']
    search_fields = ['name', 'unique_code']
    list_filter = ['subscription_active', 'subscription_date']
    readonly_fields = ['unique_code', 'subscription_date']

    def get_queryset(self, request):
        """
        Restrict queryset based on user role:
        - Super Admin: Access all restaurants.
        - Admin and other roles: Access only their related restaurant.
        """
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        elif request.user.role in ['admin', 'cook', 'waiter', 'accountant']:
            if request.user.restaurant:
                return qs.filter(id=request.user.restaurant.id)
        return qs.none()


# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'phone_number', 'address']
    search_fields = ['user__email', 'phone_number']

    def get_queryset(self, request):
        """
        Restrict the queryset based on user role:
        - Super Admin: Access all profiles.
        - Other roles: Access only profiles related to their restaurant.
        """
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        elif request.user.restaurant:
            return qs.filter(user__restaurant=request.user.restaurant)
        return qs.none()

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"
