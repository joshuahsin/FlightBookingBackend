from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from cart.models import Cart
from cart_item.models import CartItem
from cart_item.permissions import CartItemPermission
from cart_item.serializers import CartItemSerializer

CART_ITEM_LIST_CACHE_TIMEOUT = 300
CART_ITEM_LIST_CACHE_KEY = "flightbooking:cart_item_list"

def _cart_item_list_cache_key(user_id):
    return f"flightbooking:cart_item_list:user_{user_id}"

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [CartItemPermission]

    def _invalidate_cart_item_list_cache(self, key):
        cache.delete(key)

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

    def list(self, request, *args, **kwargs):
        cache_key = _cart_item_list_cache_key(request.user.id)
        cached = cache.get(cache_key)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response
        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            cache.set(cache_key, response.data, CART_ITEM_LIST_CACHE_TIMEOUT)
        response["X-Cache"] = "MISS"
        return response

    def _invalidate_cart_item_list_cache(self, user_id):
        cache.delete(_cart_item_list_cache_key(user_id))

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
        self._invalidate_cart_item_list_cache(self.request.user.id)

    def perform_update(self, serializer):
        instance = serializer.instance
        serializer.save(cart=instance.cart)
        self._invalidate_cart_item_list_cache(instance.cart.user_id)

    def perform_destroy(self, instance):
        instance.delete()
        self._invalidate_cart_item_list_cache(instance.cart.user_id)