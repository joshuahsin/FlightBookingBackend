from rest_framework import serializers

from cabin_class.models import CabinClass
from cabin_class.serializers import CabinClassEmbeddedSerializer
from fare.models import Fare
from flight.models import Flight
from flight.serializers import FlightSerializer


class FareSerializer(serializers.ModelSerializer):
    # Writable on POST/PUT (accept IDs)
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    cabin_class = serializers.PrimaryKeyRelatedField(queryset=CabinClass.objects.all())

    class Meta:
        model = Fare
        fields = '__all__'

    def to_representation(self, instance):
        """Output nested flight and cabin_class when reading."""
        data = super().to_representation(instance)
        data['flight'] = FlightSerializer(instance.flight).data
        data['cabin_class'] = CabinClassEmbeddedSerializer(instance.cabin_class).data
        return data


class FareEmbeddedSerializer(serializers.ModelSerializer):
    cabin_class = CabinClassEmbeddedSerializer()
    class Meta:
        model = Fare
        fields = ['id', 'cabin_class', 'fare_price']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['cabin_class'] = CabinClassEmbeddedSerializer(instance.cabin_class).data
        return data