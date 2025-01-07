from rest_framework import viewsets, permissions
from .models import CustomUser, Restaurant, RestaurantProfile
from .serializers import CustomUserSerializer, RestaurantSerializer, RestaurantProfileSerializer
from rest_framework.permissions import BasePermission


class IsSuperAdminOrReadOnlyForAdmins(permissions.BasePermission):
    """
    Custom permission for RestaurantViewSet:
    - Super Admins: Full access (CRUD).
    - Admins: Read-only access to their restaurant.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.role == 'super_admin' or user.is_superuser:
            return True
        if user.role == 'admin' and view.action in ['list', 'retrieve']:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'super_admin' or user.is_superuser:
            return True
        if user.role == 'admin':
            return obj == user.restaurant
        return False


class IsSuperAdminOrAdminForStaff(permissions.BasePermission):
    """
    Custom permission for CustomUserViewSet:
    - Super Admins: Full access (CRUD).
    - Admins: Manage staff accounts for their restaurant only.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser or user.role in ['super_admin', 'admin']:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.role == 'super_admin':
            return True
        if user.role == 'admin':
            return obj.restaurant == user.restaurant
        return False


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing CustomUser:
    - Super Admins: Full CRUD for all users.
    - Admins: Full CRUD for staff accounts (cook, waiter, accountant) of their restaurant.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [IsSuperAdminOrAdminForStaff]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin' or user.is_superuser:
            return CustomUser.objects.all()
        if user.role == 'admin':
            return CustomUser.objects.filter(
                restaurant=user.restaurant, role__in=['cook', 'waiter', 'accountant']
            )
        return CustomUser.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'admin':
            serializer.save(restaurant=user.restaurant, created_by=user)
        else:
            serializer.save(created_by=user)

    def perform_update(self, serializer):
        serializer.save()


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing Restaurants:
    - Super Admins: Full CRUD for all restaurants.
    - Admins: Read-only access to their restaurant.
    """
    serializer_class = RestaurantSerializer
    permission_classes = [IsSuperAdminOrReadOnlyForAdmins]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin' or user.is_superuser:
            return Restaurant.objects.all()
        if user.role == 'admin':
            return Restaurant.objects.filter(id=user.restaurant.id)
        return Restaurant.objects.none()


class RestaurantProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Profiles:
    - Super Admins: Full CRUD for all profiles.
    - Admins: Full CRUD for profiles of staff linked to their restaurant.
    """
    serializer_class = RestaurantProfileSerializer
    permission_classes = [IsSuperAdminOrAdminForStaff]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin' or user.is_superuser:
            return RestaurantProfile.objects.all()
        if user.role == 'admin':
            return RestaurantProfile.objects.filter(restaurant=user.restaurant)
        return RestaurantProfile.objects.none()

    def perform_create(self, serializer):
        serializer.save()

