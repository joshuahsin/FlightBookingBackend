from rest_framework import serializers

from cart.models import Cart
from cart.serializers import CartSerializer
from cart_item.models import CartItem
from fare.models import Fare
from fare.serializers import FareSerializer
from flight.models import Flight
from flight.serializers import FlightSerializer


class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(),
        required=False,
    )
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    fare = serializers.PrimaryKeyRelatedField(queryset=Fare.objects.all())

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'flight', 'fare', 'quantity']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['cart'] = CartSerializer(instance.cart).data
        data['flight'] = FlightSerializer(instance.flight).data
        data['fare'] = FareSerializer(instance.fare).data
        return data