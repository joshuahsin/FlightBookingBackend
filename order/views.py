from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from order.serializers import OrderSerializer
from order.models import Order
from user.permissions import IsUserOrAdmin


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"  # or role == "admin"

    #def retrieve(self, request, pk=None):
        #if self.is_admin() == False:
            #return Order.objects.get_queryset().filter(user=self.request.user)


    def get_queryset(self):
        queryset = Order.objects.select_related("user", "order_status")
        if self.is_admin():
            return queryset.all()
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admin cannot create a booking.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        order = self.get_object()

        if self.is_admin():
            raise PermissionDenied("Admin cannot update a booking.")

        if order.order_status.is_terminal == True:
            raise PermissionDenied("The booking is terminal.")

        allowed_fields = {"order_status"}
        incoming_fields = set(serializer.validated_data.keys())

        if not incoming_fields.issubset(allowed_fields):
            raise PermissionDenied("You may only update booking status")

    def perform_destroy(self, instance):
        raise PermissionDenied("Orders cannot be destroyed for archive purposes.")




