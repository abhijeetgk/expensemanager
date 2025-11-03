"""
Custom permissions for role-based access control.

Demonstrates:
- Custom DRF permissions
- Role-based access control
- Object-level permissions
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission class for admin users only."""
    
    def has_permission(self, request, view):
        """Check if user is admin."""
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission class allowing read-only for all, write for admins."""
    
    def has_permission(self, request, view):
        """Check permissions based on request method."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_admin


class IsPowerUserOrAdmin(permissions.BasePermission):
    """Permission class for power users and admins."""
    
    def has_permission(self, request, view):
        """Check if user is power user or admin."""
        return (
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_power_user)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class allowing owners to access their own objects,
    and admins to access all objects.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user owns the object or is admin."""
        if request.user.is_admin:
            return True
        
        # Check if object has created_by field
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class CanManageUsers(permissions.BasePermission):
    """Permission for user management operations."""
    
    def has_permission(self, request, view):
        """Check if user can manage users."""
        return (
            request.user.is_authenticated and
            request.user.can_manage_users()
        )


class CanManageCategories(permissions.BasePermission):
    """Permission for category management operations."""
    
    def has_permission(self, request, view):
        """Check if user can manage categories."""
        return (
            request.user.is_authenticated and
            request.user.can_manage_categories()
        )


class CanCreateCategories(permissions.BasePermission):
    """Permission for on-the-fly category creation."""
    
    def has_permission(self, request, view):
        """Check if user can create categories."""
        return (
            request.user.is_authenticated and
            request.user.can_create_categories()
        )

