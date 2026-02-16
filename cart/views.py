from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from cart.models import Cart
from cart.serializers import CartSerializer
from user.permissions import IsUserOrAdmin


# Create your views here.
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"  # or role == "admin"

    def get_queryset(self):
        # Users only see their own carts
        return Cart.objects.select_related("user").filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        # Admin cannot create carts
        if self.is_admin():
            raise PermissionDenied(
                "Admin cannot create a cart. Only users with role 'user' can create carts."
            )

        # User can only create one active cart at a time
        existing = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if existing:
            raise PermissionDenied(
                f"You already have an active cart (id={existing.id}). Use that cart or deactivate it first."
            )

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admin cannot update a cart.")
        serializer.save(user=self.request.user, is_active=True, updated_at=timezone.now())

    '''def perform_destroy(self, instance):
        # Users can only delete their own cart
        if not self.is_admin() and instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this cart.")
        instance.delete()'''