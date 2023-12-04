from rest_framework.permissions import BasePermission, SAFE_METHODS

from api.constants import STUFF_LIST


def is_safe_method(request):
    return request.method in SAFE_METHODS


def is_admin(request):
    return (
        request.user.is_authenticated
        and request.user.users_role.role == 'admin'
        or request.user.is_superuser
    )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or is_admin(request)
        )


class IsStuffOrAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(obj)
        return request.method in SAFE_METHODS or (
            request.user.is_superuser
            or request.user.users_role.role in STUFF_LIST
            or request.user == obj.user
        )
