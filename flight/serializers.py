from zoneinfo import ZoneInfo

from rest_framework import serializers

from airport.serializers import AirportSerializer
from flight.models import Flight


class FlightSerializer(serializers.ModelSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    departure_date_time = serializers.SerializerMethodField()
    arrival_date_time = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = '__all__'

    def get_departure_date_time(self, obj):
        tz = ZoneInfo(obj.departure_airport.time_zone)
        return obj.departure_date_time.astimezone(tz).isoformat()

    def get_arrival_date_time(self, obj):
        tz = ZoneInfo(obj.arrival_airport.time_zone)
        return obj.arrival_date_time.astimezone(tz).isoformat()