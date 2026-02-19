from rest_framework import serializers

from order.models import Order
from order_status.models import OrderStatus
from order_status.serializers import OrderStatusEmbeddedSerializer
from user.models import User
from user.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )
    order_status = serializers.PrimaryKeyRelatedField(
        queryset=OrderStatus.objects.all()
    )

    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data if instance.user else None
        data['order_status'] = (
            OrderStatusEmbeddedSerializer(instance.order_status).data
            if instance.order_status else None
        )
        return data