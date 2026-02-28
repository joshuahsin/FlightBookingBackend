from django.contrib.auth import get_user_model
from rest_framework import serializers

from booking.models import Booking
from booking_status.models import BookingStatus
from booking_status.serializers import BookingStatusEmbeddedSerializer
from flight.models import Flight
from flight.serializers import FlightSerializer
from order.models import Order
from order.serializers import OrderSerializer
from passenger.models import Passenger
from passenger.serializers import PassengerSerializer
from seat.models import Seat
from seat.serializers import SeatSerializer
from user.serializers import UserSerializer

User = get_user_model()


class BookingForOrderSerializer(serializers.ModelSerializer):
    """Use when nesting bookings inside an order (avoids recursion)."""
    class Meta:
        model = Booking
        fields = ['id', 'order', 'flight', 'user', 'passenger', 'seat', 'booking_status']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['flight'] = FlightSerializer(instance.flight).data
        data['passenger'] = PassengerSerializer(instance.passenger).data
        data['seat'] = SeatSerializer(instance.seat).data
        data['booking_status'] = BookingStatusEmbeddedSerializer(
            instance.booking_status
        ).data
        data['user'] = UserSerializer(instance.user).data if instance.user else None
        return data


class BookingSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True
    )
    passenger = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())
    booking_status = serializers.PrimaryKeyRelatedField(
        queryset=BookingStatus.objects.all()
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'order', 'flight', 'user', 'passenger',
            'seat', 'booking_status'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['order'] = OrderSerializer(instance.order).data
        data['flight'] = FlightSerializer(instance.flight).data
        data['user'] = UserSerializer(instance.user).data if instance.user else None
        data['passenger'] = PassengerSerializer(instance.passenger).data
        data['seat'] = SeatSerializer(instance.seat).data
        data['booking_status'] = BookingStatusEmbeddedSerializer(
            instance.booking_status
        ).data
        return data