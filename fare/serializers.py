from rest_framework import serializers

from cabin_class.serializers import CabinClassSerializer
from flight.serializers import FlightSerializer
from fare.models import Fare


class FareSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    cabin_class = CabinClassSerializer(read_only=True)
    class Meta:
        model = Fare
        fields = '__all__'