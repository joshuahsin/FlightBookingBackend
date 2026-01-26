from rest_framework import serializers
from .models import Airport
from city.serializers import CitySerializer

class AirportSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    
    class Meta:
        model = Airport
        fields = '__all__'