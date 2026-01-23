from django.shortcuts import render
from rest_framework import viewsets

from payment_status.models import PaymentStatus
from payment_status.serializers import PaymentStatusSerializer
from user.permissions import IsAdminOrReadOnly


# Create your views here.
class PaymentStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentStatus.objects.all()
    serializer_class = PaymentStatusSerializer



