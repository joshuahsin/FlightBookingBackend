from django.core.cache import cache
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from cart.models import Cart
from cart.serializers import CartSerializer
from user.permissions import IsUserOrAdmin

CART_LIST_CACHE_TIMEOUT = 300
CART_LIST_CACHE_KEY = "flightbooking:cart_list"

def _cart_list_cache_key(user_id):
    return f"flightbooking:cart_list:user_{user_id}"

# Create your views here.
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"  # or role == "admin"

    def _invalidate_cart_list_cache(self):
        cache.delete(AIRPORT_LIST_CACHE_KEY)

    def get_queryset(self):
        # Users only see their own carts
        cache_key = _cart_list_cache_key(self.request.user.id)
        cached = cache.get(cache_key)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response
        cache.set(cache_key, response.data, CART_LIST_CACHE_TIMEOUT)
        queryset = Cart.objects.select_related("user").filter(user=self.request.user, is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(CART_LIST_CACHE_KEY, data, CART_LIST_CACHE_TIMEOUT)
        response = Response(data)
        response["X-Cache"] = "MISS"
        return response

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
        self._invalidate_cart_list_cache()

    def perform_update(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admin cannot update a cart.")
        serializer.save(user=self.request.user, is_active=True, updated_at=timezone.now())
        self._invalidate_cart_list_cache()

    def perform_destroy(self, instance):
        # Users can only delete their own cart
        if not self.is_admin() and instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this cart.")
        instance.delete()