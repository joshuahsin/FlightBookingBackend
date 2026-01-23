from rest_framework import serializers
from cart.models import Cart
from user.serializers import UserSerializer


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = '__all__'