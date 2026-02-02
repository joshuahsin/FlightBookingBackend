from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUser(BasePermission):
    message = "You must be logged in to access this resource."

    def has_permission(self, request, view):
        print("USER:", request.user)
        print("AUTH:", request.auth)
        if(request.user == AnonymousUser()):
            return False
        elif(request.user and request.user.role=="user"):
            return request.user.is_authenticated
        else:
            return False

class IsAdmin(BasePermission):
    message = "You must be logged in to access this resource."

    def has_permission(self, request, view):
        print("USER:", request.user)
        print("AUTH:", request.auth)
        if(request.user == AnonymousUser()):
            return False
        elif(request.user and request.user.role == "admin"):
            return request.user.is_authenticated
        else:
            return False

class IsUserOrAdmin(BasePermission):
    message = "You must be logged in to access this resource."

    def has_permission(self, request, view):
        if(request.user == AnonymousUser()):
            return False
        elif(request.user and (request.user.role == "user" or request.user.role == "admin")):
            return request.user.is_authenticated
        else:
            return False

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.role == "admin"


class UserPermission(BasePermission):
    """
    - Create: no auth required (anyone can register).
    - List/Retrieve: authenticated; admin sees all, user sees only own (via get_queryset + object).
    - Update/Delete: user can only act on own account; admin cannot edit or delete users.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if view.action == "create":
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            if request.user.role == "admin":
                return True
            return obj.id == request.user.id
        if view.action in ("update", "partial_update", "destroy"):
            if request.user.role == "admin":
                return False
            return obj.id == request.user.id
        return False