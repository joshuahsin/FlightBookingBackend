from rest_framework import serializers

from payment_status.models import PaymentStatus


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = '__all__'

class PaymentStatusEmbeddedSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = ['id', 'code', 'is_terminal']