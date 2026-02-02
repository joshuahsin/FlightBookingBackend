from rest_framework import serializers

from cart.models import Cart
from user.models import User
from user.serializers import UserSerializer


class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True
    )

    class Meta:
        model = Cart
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data if instance.user else None
        return data