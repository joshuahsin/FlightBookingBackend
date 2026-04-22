from rest_framework import serializers

from refund_request.models import RefundRequest


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = ['id', 'order', 'booking', 'status', 'reason', 'requested_at', 'processed_at']
        read_only_fields = ['status', 'requested_at', 'processed_at']
