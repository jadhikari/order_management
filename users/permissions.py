from rest_framework.permissions import BasePermission


class IsSuperAdminOrRestaurantUser(BasePermission):
    """
    Custom permission to restrict data access:
    - Super Admin: Can access all data.
    - Admin, Cook, Waiter, Accountant: Can access only their restaurant's data.
    """

    def has_permission(self, request, view):
        user = request.user

        # Allow super_admins to access all data
        if getattr(user, 'role', None) == 'super_admin':
            return True

        # Allow access to users with an associated restaurant
        return getattr(user, 'restaurant', None) is not None

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow super_admins to access all objects
        if getattr(user, 'role', None) == 'super_admin':
            return True

        # Check if the object is associated with a restaurant
        if hasattr(obj, 'restaurant') and obj.restaurant:
            return obj.restaurant == getattr(user, 'restaurant', None)

        return False
