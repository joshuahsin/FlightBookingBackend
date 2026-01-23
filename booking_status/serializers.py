from rest_framework import serializers

from booking_status.models import BookingStatus


class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStatus
        fields = '__all__'

class BookingStatusEmbeddedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStatus
        fields = ['id', 'code', 'is_terminal']