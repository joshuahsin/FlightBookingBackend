from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from payment.models import Payment
from payment.serializers import PaymentSerializer
from user.permissions import IsUserOrAdmin


# Create your views here.
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"

    def get_queryset(self):
        queryset = Payment.objects.select_related("order", "payment_status")
        if self.is_admin() == False:
            return queryset.filter(order__user=self.request.user)
        return queryset.all()

    def perform_create(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admins cannot create payments")
        print(serializer.data)
        order = serializer.validated_data.get("order")

        if order.user != self.request.user:
            raise PermissionDenied("You cannot pay for another user's order")

        serializer.save()

    def perform_update(self, serializer):
        if self.is_admin():
            raise PermissionDenied("You don't have permission to perform this action")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied("Orders cannot be deleted.")