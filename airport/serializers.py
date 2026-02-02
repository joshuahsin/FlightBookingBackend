from rest_framework import serializers

from city.models import City
from city.serializers import CitySerializer
from .models import Airport


class AirportSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    class Meta:
        model = Airport
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['city'] = CitySerializer(instance.city).data
        return data