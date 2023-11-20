"""Классы разрешений для приложения API."""
from rest_framework import permissions


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """Класс для контроля доступа к административным данным."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class AdminOnlyPermission(permissions.BasePermission):
    """Класс для контроля доступа к административным данным."""

    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_staff


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """IsAuthorModeratorAdminOrReadOnly permission.
    1) Разрешает доступ к ресурсу, если используется безопасный метод или в
    случае, когда пользователь аутентифицирован.
    2) Разрешает доступ к объекту в случаях, когда используется безопасный
    метод или пользователь - это автор объекта, имеет роль
    модератора, администратора или суперпользователя.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role in ('moderator', 'admin')
            or request.user.is_superuser
        )
