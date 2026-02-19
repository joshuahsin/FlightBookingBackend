from django.core.cache import cache
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from order.serializers import OrderSerializer
from order.models import Order
from user.permissions import IsUserOrAdmin

ORDER_LIST_CACHE_TIMEOUT = 300
ORDER_LIST_FILTER_PARAMS = ("user_id")
ORDER_LIST_CACHE_KEY = "flightbooking:order_list"

def _order_list_cache_key(user_id):
    return f"flightbooking:order_list:user_{user_id}"

# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"

    def _invalidate_order_list_cache(self, user_id):
        cache.delete(_order_list_cache_key(user_id))
    
    def _invalidate_admin_order_list_cache(self):
        cache.delete(_order_list_cache_key)

    def get_queryset(self):
        queryset = Order.objects.select_related("user", "order_status")
        if self.is_admin():
            # Admin can filter by user_id via ?user_id=...
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            return queryset
        # Non-admin: only their own orders
        return queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        if self.is_admin():
            if "user_id" not in request.query_params:
                cached = cache.get(ORDER_LIST_CACHE_KEY)
                if cached is not None:
                    response = Response(cached)
                    response["X-Cache"] = "HIT"
                    return response
                queryset = self.get_queryset()
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
                cache.set(ORDER_LIST_CACHE_KEY, data, ORDER_LIST_CACHE_TIMEOUT)
                response = Response(data)
                response["X-Cache"] = "MISS"
                return response
            else:
                cache_key = _order_list_cache_key(request.query_params.get("user_id"))
                cached = cache.get(cache_key)
                if cached is not None:
                    response = Response(cached)
                    response["X-Cache"] = "HIT"
                    return response
                queryset = self.get_queryset()
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
                cache.set(cache_key, data, ORDER_LIST_CACHE_TIMEOUT)
                response = Response(data)
                response["X-Cache"] = "MISS"
                return response
        else:
            cache_key = _order_list_cache_key(self.request.user.id)
            cached = cache.get(cache_key)
            if cached is not None:
                data = Response(cached)
                data["X-Cache"] = "HIT"
                return data
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, ORDER_LIST_CACHE_TIMEOUT)
            response = Response(data)
            response["X-Cache"] = "MISS"
            return response

    def perform_create(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admin cannot create an order.")
        serializer.save(user=self.request.user)
        self._invalidate_order_list_cache(self.request.user.id)
        self._invalidate_admin_order_list_cache()

    def perform_update(self, serializer):
        order = self.get_object()

        if self.is_admin():
            raise PermissionDenied("Admin cannot update a order.")

        if order.order_status.is_terminal == True:
            raise PermissionDenied("The order is terminal.")
        
        if order.user != self.request.user:
            raise PermissionDenied("Not your order")

        allowed_fields = {"order_status"}
        incoming_fields = set(serializer.validated_data.keys())

        if not incoming_fields.issubset(allowed_fields):
            raise PermissionDenied("You may only update order status")
        serializer.save()
        self._invalidate_order_list_cache(order.user_id)
        self._invalidate_admin_order_list_cache()

    def perform_destroy(self, instance):
        raise PermissionDenied("Orders cannot be destroyed for archive purposes.")




