import string
import random

from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from order.models import Order
from order.serializers import OrderSerializer
from booking.serializers import BookingForOrderSerializer
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
        confirmation_number = self._generate_order_confirmation_number()
        serializer.save(user=self.request.user, confirmation_number=confirmation_number)
        self._invalidate_order_list_cache(self.request.user.id)
        self._invalidate_admin_order_list_cache()

    def _generate_order_confirmation_number(self):
        while True:
            chars = string.ascii_uppercase + string.digits
            value = ''.join(random.choices(chars, k=6))
            if not Order.objects.filter(confirmation_number=value).exists():
                return value

    @action(detail=False, methods=['get'], url_path='lookup', permission_classes=[AllowAny])
    def lookup(self, request):
        """Find order by confirmation_number + last_name; returns order with nested bookings."""
        confirmation_number = request.query_params.get('confirmation_number')
        last_name = request.query_params.get('last_name')
        if not confirmation_number or not last_name:
            return Response(
                {'detail': 'confirmation_number and last_name are required.'},
                status=400
            )
        order = (
            Order.objects
            .filter(confirmation_number__iexact=confirmation_number.strip())
            .filter(bookings__passenger__last_name__iexact=last_name.strip())
            .distinct()
            .prefetch_related(
                'bookings__flight',
                'bookings__passenger',
                'bookings__seat',
                'bookings__booking_status',
            )
            .select_related('user', 'order_status')
            .first()
        )
        if not order:
            return Response({'detail': 'Order not found.'}, status=404)
        data = OrderSerializer(order).data
        data['bookings'] = BookingForOrderSerializer(order.bookings.all(), many=True).data
        return Response(data)

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




