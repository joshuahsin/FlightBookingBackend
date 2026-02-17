from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from cart.models import Cart
from cart_item.models import CartItem
from cart_item.permissions import CartItemPermission
from cart_item.serializers import CartItemSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [CartItemPermission]

    def get_queryset(self):
        # Only return cart items that belong to the current user's carts
        return CartItem.objects.select_related(
            "flight",
            "flight__departure_airport",
            "flight__departure_airport__city",
            "flight__arrival_airport",
            "flight__arrival_airport__city",
            "fare",
            "fare__cabin_class",
        ).filter(cart__user=self.request.user, cart__is_active=True)

    def perform_create(self, serializer):
        # User comes from the access token (request.user). Use their active cart.
        cart = serializer.validated_data.get("cart")
        if cart and cart.user_id != self.request.user.id:
            raise PermissionDenied("You can only add items to your own cart.")
        if not cart:
            cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
            if not cart:
                raise ValidationError({"cart": "You have no active cart. Create a cart first."})
        serializer.save(cart=cart)