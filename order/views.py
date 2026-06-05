import string
import random

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from booking_status.models import BookingStatus
from order.models import Order
from order.serializers import OrderSerializer
from order_status.models import OrderStatus
from booking.serializers import BookingForOrderSerializer
from user.permissions import IsUserOrAdmin
from flightsite.cache_keys import booking_list_cache_key as _booking_list_cache_key
from flightsite.cache_keys import order_list_cache_key as _order_list_cache_key

ORDER_LIST_CACHE_TIMEOUT = 300

# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"

    def _invalidate_order_list_cache(self, user_id):
        cache.delete(_order_list_cache_key(user_id))

    def get_queryset(self):
        return Order.objects.none()

    def list(self, request, *args, **kwargs):
        if self.is_admin():
            if not request.query_params.get("email") and not request.query_params.get("confirmation_number"):
                return Response({'detail': 'Provide at least one filter: email or confirmation_number.'}, status=400)
            queryset = Order.objects.select_related("user", "order_status")
            if email := request.query_params.get("email"):
                queryset = queryset.filter(user__email__iexact=email.strip())
            if confirmation_number := request.query_params.get("confirmation_number"):
                queryset = queryset.filter(confirmation_number__iexact=confirmation_number.strip())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        cache_key = _order_list_cache_key(request.user.id)
        cached = cache.get(cache_key)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response
        queryset = Order.objects.select_related("user", "order_status").filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, ORDER_LIST_CACHE_TIMEOUT)
        response = Response(serializer.data)
        response["X-Cache"] = "MISS"
        return response

    def perform_create(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admin cannot create an order.")
        confirmation_number = self._generate_order_confirmation_number()
        serializer.save(user=self.request.user, confirmation_number=confirmation_number)
        self._invalidate_order_list_cache(self.request.user.id)
        cache.delete(_booking_list_cache_key(self.request.user.id))

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
        raise PermissionDenied("Use the /cancel action to update an order.")

    def perform_destroy(self, instance):
        raise PermissionDenied("Orders cannot be destroyed for archive purposes.")

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = get_object_or_404(Order.objects.select_related('order_status'), pk=pk)

        if self.is_admin():
            raise PermissionDenied("Admin cannot cancel an order.")

        if order.user_id != request.user.id:
            raise PermissionDenied("Not your order.")

        if order.order_status.is_terminal:
            raise PermissionDenied("Order is already in a terminal state.")

        cancelled_order_status = OrderStatus.objects.filter(code='CANCELLED').first()
        if cancelled_order_status is None:
            return Response({'detail': 'CANCELLED order status not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        cancelled_booking_status = BookingStatus.objects.filter(code='CANCELLED').first()
        if cancelled_booking_status is None:
            return Response({'detail': 'CANCELLED booking status not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        order.order_status = cancelled_order_status
        order.save()

        order.bookings.filter(booking_status__is_terminal=False).update(booking_status=cancelled_booking_status)

        self._invalidate_order_list_cache(order.user_id)
        cache.delete(_booking_list_cache_key(order.user_id))

        return Response(OrderSerializer(order).data)





