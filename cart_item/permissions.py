from rest_framework.permissions import BasePermission


class CartItemPermission(BasePermission):
    """
    Users can only view, edit, and delete their own cart items (items in their cart).
    """
    message = "You can only access your own cart items."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.cart.user_id == request.user.id
