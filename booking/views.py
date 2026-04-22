from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from booking.models import Booking
from booking.serializers import BookingSerializer
from booking_status.models import BookingStatus
from user.permissions import IsUserOrAdmin

BOOKING_LIST_CACHE_TIMEOUT = 300
BOOKING_LIST_FILTER_PARAMS = ("booking_status",)


def _booking_list_cache_key(user_id):
    return f"flightbooking:booking_list:user_{user_id}"

# Create your views here.
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"  # or role == "admin"

    def _invalidate_user_booking_list_cache(self, user_id):
        cache.delete(_booking_list_cache_key(user_id))

    def get_queryset(self):
        # Admin users → full search
        if self.request.user.role == "admin":
            return self.admin_queryset()

        # Public users → restricted lookup
        return self.public_queryset()

    def list(self, request, *args, **kwargs):
        # Cache only when no filter params (plain "my bookings")
        no_filters = not any(request.query_params.get(p) for p in BOOKING_LIST_FILTER_PARAMS)
        if request.user.role != "admin" and no_filters:
            cache_key = _booking_list_cache_key(request.user.id)
            cached = cache.get(cache_key)
            if cached is not None:
                response = Response(cached)
                response["X-Cache"] = "HIT"
                return response
            response = super().list(request, *args, **kwargs)
            if response.status_code == 200:
                cache.set(cache_key, response.data, BOOKING_LIST_CACHE_TIMEOUT)
            response["X-Cache"] = "MISS"
            return response
        return super().list(request, *args, **kwargs)

    def _optimized_queryset(self, queryset):
        # One query with JOINs; avoids N+1 when serializer accesses order, flight, passenger, seat, booking_status
        return queryset.select_related(
            "order", "flight", "passenger", "seat", "booking_status"
        )

    def public_queryset(self):
        queryset = super().get_queryset()
        # "My bookings" = bookings whose order belongs to the current user (no Booking.user needed)
        queryset = self._optimized_queryset(queryset).filter(order__user=self.request.user)

        if self.action == "list":
            params = self.request.query_params
            if booking_status := params.get("booking_status"):
                queryset = queryset.filter(
                    booking_status__code__exact=booking_status.strip().upper()
                )
            return queryset

        # retrieve / update / delete by ID
        return queryset

    def admin_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        if order_cn := params.get("confirmation_number"):
            queryset = queryset.filter(order__confirmation_number__iexact=order_cn)

        if first_name := params.get("first_name"):
            queryset = queryset.filter(passenger__first_name__iexact=first_name)

        if last_name := params.get("last_name"):
            queryset = queryset.filter(passenger__last_name__iexact=last_name)

        if status := params.get("booking_status"):
            queryset = queryset.filter(booking_status__code__iexact=status)

        if flight_number := params.get("flight_number"):
            queryset = queryset.filter(flight__id__iexact=flight_number)

        if start_date := params.get("start_date"):
            queryset = queryset.filter(flight__departure_date_time__gte=start_date)

        if end_date := params.get("end_date"):
            queryset = queryset.filter(flight__departure_date_time__lte=end_date)

        return self._optimized_queryset(queryset)

    def perform_create(self, serializer):
        # Admin cannot create bookings
        if self.is_admin():
            raise PermissionDenied("Admin cannot create a booking.")
        serializer.save()
        # Invalidate cache for the order owner (current user created the booking for their order)
        self._invalidate_user_booking_list_cache(self.request.user.id)

    def perform_update(self, serializer):
        raise PermissionDenied("Use the /cancel action to update a booking.")

    def perform_destroy(self, instance):
        raise PermissionDenied("Bookings cannot be deleted for archive purposes.")

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if self.is_admin():
            raise PermissionDenied("Admin cannot cancel a booking.")

        if booking.order.user_id != request.user.id:
            raise PermissionDenied("Not your booking.")

        if booking.booking_status.is_terminal:
            raise PermissionDenied("Booking is already in a terminal state.")

        cancelled_status = BookingStatus.objects.filter(code='CANCELLED').first()
        if cancelled_status is None:
            return Response({'detail': 'CANCELLED booking status not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        booking.booking_status = cancelled_status
        booking.save()

        self._invalidate_user_booking_list_cache(booking.order.user_id)

        return Response(BookingSerializer(booking, context={'request': request}).data)