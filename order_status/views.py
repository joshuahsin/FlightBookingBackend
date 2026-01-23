from django.shortcuts import render
from django.views import View
from rest_framework import viewsets

from order_status.models import OrderStatus
from order_status.serializers import OrderStatusSerializer
from user.permissions import IsAdminOrReadOnly


# Create your views here.
class OrderStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderStatus.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [IsAdminOrReadOnly]