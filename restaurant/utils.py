from rest_framework import permissions


class IsRestaurantOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_restaurant_owner:
            return True
        return False


class MenuPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_employee or request.user.is_restaurant_owner:
            return True
        return False


class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_restaurant_owner:
            return False
        if request.user.is_employee:
            return True
        return False
