from rest_framework import serializers

from booking.models import Booking
from booking_status.serializers import BookingStatusEmbeddedSerializer
from flight.serializers import FlightSerializer
from order.serializers import OrderSerializer
from passenger.serializers import PassengerSerializer
from seat.serializers import SeatSerializer
from user.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    #flight = FlightSerializer(read_only=True)
    #user = UserSerializer(read_only=True)
    passenger = PassengerSerializer(read_only=True)
    seat = SeatSerializer(read_only=True)
    booking_status = BookingStatusEmbeddedSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'seat', 'passenger', 'order', 'booking_status']