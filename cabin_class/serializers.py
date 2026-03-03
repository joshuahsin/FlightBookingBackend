from rest_framework import serializers
from cabin_class.models import CabinClass


class CabinClassSerializer(serializers.ModelSerializer):
    """Full serializer for cabin_class list/detail (includes id for creating fares/seats)."""
    class Meta:
        model = CabinClass
        fields = '__all__'


class CabinClassEmbeddedSerializer(serializers.ModelSerializer):
    """Minimal representation when nested in seat/fare: just the name for display."""
    class Meta:
        model = CabinClass
        fields = ['cabin_class_name']