from rest_framework.permissions import BasePermission


class IsSuperAdminOrRestaurantUser(BasePermission):
    """
    Custom permission to restrict data access:
    - Super Admin: Can access all data.
    - Admin, Cook, Waiter, Accountant: Can access only their restaurant's data.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.role == 'super_admin':
            return True
        return hasattr(user, 'restaurant') and user.restaurant is not None

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'super_admin':
            return True
        if hasattr(obj, 'restaurant') and obj.restaurant:
            return obj.restaurant == user.restaurant
        return False
