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
        if self.is_admin():
            # Admin can see ALL carts
            queryset = super().get_queryset()
            params = self.request.query_params

            if first_name := params.get("first_name"):
                queryset = queryset.filter(user__first_name__icontains=first_name)

            if last_name := params.get("last_name"):
                queryset = queryset.filter(user__last_name__icontains=last_name)

            if is_active := params.get("is_active"):
                queryset = queryset.filter(is_active=is_active.lower() == "true")

            return queryset

        # Users only see their own carts
        return Cart.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        # Admin cannot create carts
        if self.is_admin():
            raise PermissionDenied("Admin cannot create a cart.")

        # User can only create a cart if they don't already have an active one
        if Cart.objects.filter(user=self.request.user, is_active=True).exists():
            raise PermissionDenied("You already have an active cart.")

        serializer.save(user=self.request.user)

    '''def perform_destroy(self, instance):
        # Users can only delete their own cart
        if not self.is_admin() and instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this cart.")
        instance.delete()'''