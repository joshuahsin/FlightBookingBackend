from django.core.cache import cache
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from cart.models import Cart
from cart.serializers import CartSerializer
from user.permissions import IsUserOrAdmin

CART_LIST_CACHE_TIMEOUT = 300


def _cart_list_cache_key(user_id):
    return f"flightbooking:cart_list:user_{user_id}"


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"

    def get_queryset(self):
        return Cart.objects.select_related("user").filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        if request.user.role == "admin":
            raise PermissionDenied("Admin cannot view carts.")
        cache_key = _cart_list_cache_key(request.user.id)
        cached = cache.get(cache_key)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response
        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            cache.set(cache_key, response.data, CART_LIST_CACHE_TIMEOUT)
        response["X-Cache"] = "MISS"
        return response

    def _invalidate_cart_list_cache(self, user_id):
        cache.delete(_cart_list_cache_key(user_id))

    def perform_create(self, serializer):
        # Admin cannot create carts
        if self.is_admin():
            raise PermissionDenied(
                "Admin cannot create a cart. Only users with role 'user' can create carts."
            )

        Cart.objects.filter(user=self.request.user).delete()

        serializer.save(user=self.request.user)
        self._invalidate_cart_list_cache(self.request.user.id)

    def perform_update(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admin cannot update a cart.")
        instance = serializer.instance
        serializer.save(user=self.request.user, updated_at=timezone.now())
        self._invalidate_cart_list_cache(instance.user_id)

    def perform_destroy(self, instance):
        if not self.is_admin() and instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this cart.")
        user_id = instance.user_id
        instance.delete()
        self._invalidate_cart_list_cache(user_id)