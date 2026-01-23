from rest_framework import serializers

from order.models import Order
from order.serializers import OrderSerializer
from payment.models import Payment
from payment_status.serializers import PaymentStatusSerializer, PaymentStatusEmbeddedSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        write_only=True
    )
    order_detail = OrderSerializer(source="order", read_only=True)
    payment_status = PaymentStatusEmbeddedSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = '__all__'

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