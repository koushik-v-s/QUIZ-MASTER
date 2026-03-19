"""
Custom permission classes for the Quiz App.
Implements strict role-based access as defined in the master prompt.
"""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access only to users with role='admin'.
    Users get 403.
    """
    message = 'Only admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsUserRole(BasePermission):
    """
    Allows access only to users with role='user'.
    Admins get 403 with a clear message.
    """
    message = 'Admins cannot attempt quizzes. Use a user account.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'user'
        )


class IsQuizOwner(BasePermission):
    """
    Object-level: only the admin who created this quiz can edit/delete it.
    """
    message = 'You do not own this quiz.'

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class IsQuizOwnerOrSuperAdmin(BasePermission):
    """
    Quiz owner OR superuser (initial seed admin) can modify.
    """
    message = 'You do not have permission to modify this quiz.'

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.is_superuser


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allows access to the owner or admin users.
    Checks for 'created_by' or 'user' attribute on the object.
    """
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAttemptOwner(BasePermission):
    """
    Object-level: only the user who owns the attempt can access it.
    """
    message = 'You do not own this attempt.'

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAuthenticatedAndVerified(BasePermission):
    """
    Standard authentication check with active user verification.
    """
    message = 'Authentication required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
        )
