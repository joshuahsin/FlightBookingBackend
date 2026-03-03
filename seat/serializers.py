from rest_framework import serializers

from cabin_class.models import CabinClass
from cabin_class.serializers import CabinClassEmbeddedSerializer
from flight.models import Flight
from flight.serializers import FlightSerializer
from seat.models import Seat


class SeatSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    cabin_class = serializers.PrimaryKeyRelatedField(queryset=CabinClass.objects.all())

    class Meta:
        model = Seat
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['flight'] = FlightSerializer(instance.flight).data
        data['cabin_class'] = CabinClassEmbeddedSerializer(instance.cabin_class).data
        return data