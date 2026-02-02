from rest_framework import serializers

from order.models import Order
from payment.models import Payment
from payment_status.models import PaymentStatus
from payment_status.serializers import PaymentStatusEmbeddedSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        required=True,
    )
    payment_status = serializers.PrimaryKeyRelatedField(
        queryset=PaymentStatus.objects.all(),
        allow_null=True
    )

    class Meta:
        model = Payment
        fields = '__all__'

    def update(self, instance, validated_data):
        # Order cannot be changed after creation
        validated_data.pop('order', None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['payment_status'] = (
            PaymentStatusEmbeddedSerializer(instance.payment_status).data
            if instance.payment_status else None
        )
        return data

    def validate(self, attrs):
        print("ATTRS:", attrs)
        return attrs

    def validate_order(self, order):
        request = self.context["request"]
        #print("request", request)
        #print("order", order)
        if order.user != request.user:
            raise serializers.ValidationError(
                "Order does not belong to you"
            )
        if order.order_status.code in ["PAID", "CONFIRMED", "CANCELLED", "REFUNDED"]:
            raise serializers.ValidationError(
                "Order has already been paid, cancelled, or refunded"
            )
        return order