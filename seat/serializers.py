from rest_framework import serializers

from cabin_class.serializers import CabinClassSerializer
from flight.serializers import FlightSerializer
from seat.models import Seat


class SeatSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    cabin_class = CabinClassSerializer(read_only=True)
    class Meta:
        model = Seat
        fields = '__all__'