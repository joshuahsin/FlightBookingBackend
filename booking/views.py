import string
import random

from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from booking.models import Booking
from booking.serializers import BookingSerializer
from user.permissions import IsUserOrAdmin

BOOKING_LIST_CACHE_TIMEOUT = 300
BOOKING_LIST_FILTER_PARAMS = ("confirmation_number", "last_name", "booking_status")


def _booking_list_cache_key(user_id):
    return f"flightbooking:booking_list:user_{user_id}"

# Create your views here.
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsUserOrAdmin]

    def generate_pnr(self):
        while True:
            chars = string.ascii_uppercase + string.digits
            chars = ''.join(random.choices(chars, k=6))
            if not Booking.objects.filter(confirmation_number=chars).exists():
                return chars

    def is_admin(self):
        return self.request.user.role == "admin"  # or role == "admin"

    #def retrieve(self, request, pk=None):
        #print("HEREEE")

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

    def _invalidate_user_booking_list_cache(self, user_id):
        cache.delete(_booking_list_cache_key(user_id))

    def _optimized_queryset(self, queryset):
        # One query with JOINs; avoids N+1 when serializer accesses order, flight, user, passenger, seat, booking_status
        return queryset.select_related(
            "user", "order", "flight", "passenger", "seat", "booking_status"
        )

    def public_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            params = self.request.query_params
            # Filter params must match BOOKING_LIST_FILTER_PARAMS (used for cache key in list())
            confirmation = params.get("confirmation_number")
            last_name = params.get("last_name")

            if confirmation and last_name:
                return self._optimized_queryset(queryset).filter(
                    confirmation_number__iexact=confirmation,
                    passenger__last_name__iexact=last_name,
                )
            queryset = self._optimized_queryset(queryset).filter(user=self.request.user)
            if booking_status := params.get("booking_status"):
                # exact + normalized: lets DB use unique index on code (iexact can prevent that)
                queryset = queryset.filter(
                    booking_status__code__exact=booking_status.strip().upper()
                )
            return queryset

        # retrieve / update / delete by ID
        return self._optimized_queryset(queryset).filter(user=self.request.user)

    def admin_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        if confirmation := params.get("confirmation_number"):
            queryset = queryset.filter(confirmation_number__icontains=confirmation)

        if first_name := params.get("first_name"):
            queryset = queryset.filter(passenger__first_name__icontains=first_name)

        if last_name := params.get("last_name"):
            queryset = queryset.filter(passenger__last_name__icontains=last_name)

        if status := params.get("booking_status"):
            queryset = queryset.filter(booking_status__code__iexact=status)

        if flight_number := params.get("flight_number"):
            queryset = queryset.filter(flight__id__icontains=flight_number)

        if start_date := params.get("start_date"):
            queryset = queryset.filter(flight__departure_date_time__gte=start_date)

        if end_date := params.get("end_date"):
            queryset = queryset.filter(flight__departure_date_time__lte=end_date)

        return self._optimized_queryset(queryset)

    def perform_create(self, serializer):
        # Admin cannot create bookings
        if self.is_admin():
            raise PermissionDenied("Admin cannot create a booking.")
        confirmation_number = self.generate_pnr()
        serializer.save(user=self.request.user, confirmation_number=confirmation_number)
        self._invalidate_user_booking_list_cache(self.request.user.id)

    def perform_update(self, serializer):
        booking = self.get_object()

        if self.is_admin():
            raise PermissionDenied("Admin cannot update a booking.")

        if booking.user != self.request.user:
            raise PermissionDenied("Not your booking")

        if booking.booking_status.is_terminal == True:
            raise PermissionDenied("Booking cannot be edited now")

        allowed_fields = {"booking_status"}
        incoming_fields = set(serializer.validated_data.keys())

        if not incoming_fields.issubset(allowed_fields):
            raise PermissionDenied("You may only update booking status")

        serializer.save()
        self._invalidate_user_booking_list_cache(booking.user_id)

    def perform_destroy(self, instance):
        raise PermissionDenied("Bookings cannot be deleted for archive purposes.")