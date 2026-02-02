from zoneinfo import ZoneInfo

from rest_framework import serializers

from airport.models import Airport
from airport.serializers import AirportSerializer
from flight.models import Flight


class FlightSerializer(serializers.ModelSerializer):
    # Writable on POST/PUT (accept airport IDs)
    departure_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    arrival_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    departure_date_time = serializers.DateTimeField()
    arrival_date_time = serializers.DateTimeField()

    class Meta:
        model = Flight
        fields = '__all__'

    def to_representation(self, instance):
        """Output nested airports and formatted datetimes when reading."""
        data = super().to_representation(instance)
        data['departure_airport'] = AirportSerializer(instance.departure_airport).data
        data['arrival_airport'] = AirportSerializer(instance.arrival_airport).data
        tz_dep = ZoneInfo(instance.departure_airport.city.time_zone)
        tz_arr = ZoneInfo(instance.arrival_airport.city.time_zone)
        data['departure_date_time'] = instance.departure_date_time.astimezone(tz_dep).isoformat()
        data['arrival_date_time'] = instance.arrival_date_time.astimezone(tz_arr).isoformat()
        return data