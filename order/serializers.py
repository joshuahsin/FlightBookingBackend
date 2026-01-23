from order.models import Order
from rest_framework import serializers

from order_status.serializers import OrderStatusEmbeddedSerializer
from user.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    order_status = OrderStatusEmbeddedSerializer(read_only=True)
    class Meta:
        model = Order
        fields = '__all__'