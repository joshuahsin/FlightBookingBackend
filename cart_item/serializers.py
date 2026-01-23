from rest_framework import serializers
from cart.serializers import CartSerializer
from cart_item.models import CartItem
from fare.serializers import FareSerializer
from flight.serializers import FlightSerializer


class CartItemSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    #flight = FlightSerializer(read_only=True)
    fare = FareSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'fare']