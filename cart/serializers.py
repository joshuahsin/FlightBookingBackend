from rest_framework import serializers

from cart.models import Cart
from user.models import User
from user.serializers import UserSerializer
from flight.serializers import FlightSerializer
from fare.serializers import FareEmbeddedSerializer
from flight.models import Flight
from fare.models import Fare


class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )
    departure_flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    return_flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all(), allow_null=True, required=False)
    departure_fare = serializers.PrimaryKeyRelatedField(queryset=Fare.objects.all())
    return_fare = serializers.PrimaryKeyRelatedField(queryset=Fare.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Cart
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data if instance.user else None
        data['departure_flight'] = FlightSerializer(instance.departure_flight).data
        if instance.return_flight:
            data['return_flight'] = FlightSerializer(instance.return_flight).data
        data['departure_fare'] = FareEmbeddedSerializer(instance.departure_fare).data
        if instance.return_fare:
            data['return_fare'] = FareEmbeddedSerializer(instance.return_fare).data
        return data