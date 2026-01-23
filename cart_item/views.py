from rest_framework import viewsets

from cart_item.models import CartItem
from cart_item.serializers import CartItemSerializer
from user.permissions import IsUserOrAdmin


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permissions_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"  # or role == "admin"

    def get_queryset(self):
        if self.is_admin():
            # Admin can see ALL carts
            return CartItem.objects.all()

        # Users only see their own carts
        return CartItem.objects.filter(user=self.request.user, is_active=True)