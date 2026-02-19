from django.core.cache import cache
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from payment.models import Payment
from payment.serializers import PaymentSerializer
from user.permissions import IsUserOrAdmin

PAYMENT_LIST_CACHE_TIMEOUT = 300

def _payment_list_cache_key(user_id):
    return f"flightbooking:payment_list:user_{user_id}"

# Create your views here.
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsUserOrAdmin]

    def is_admin(self):
        return self.request.user.role == "admin"
    
    def _invalidate_payment_list_cache(self, user_id):
        cache.delete(_payment_list_cache_key(user_id))

    def get_queryset(self):
        queryset = Payment.objects.select_related("order", "payment_status")
        if not self.is_admin():
            return queryset.filter(order__user=self.request.user)
        return queryset.all()

    def list(self, request, *args, **kwargs):
        if not self.is_admin():
            cache_key = _payment_list_cache_key(self.request.user.id)
            cached = cache.get(cache_key)
            if cached is not None:
                response = Response(cached)
                response["X-Cache"] = "HIT"
                return response
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, PAYMENT_LIST_CACHE_TIMEOUT)
            response = Response(data)
            response["X-Cache"] = "MISS"
            return response
        else:
            if "user_id" in request.query_params:
                cache_key = _payment_list_cache_key(request.query_params.get("user_id"))
                cached = cache.get(cache_key)
                if cached is not None:
                    response = Response(cached)
                    response["X-Cache"] = "HIT"
                    return response
                queryset = self.get_queryset().filter(order__user_id=request.query_params.get("user_id"))
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
                cache.set(cache_key, data, PAYMENT_LIST_CACHE_TIMEOUT)
                response = Response(data)
                response["X-Cache"] = "MISS"
                return response
            else:
                return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.is_admin():
            raise PermissionDenied("Admins cannot create payments")
        order = serializer.validated_data.get("order")

        if order.user != self.request.user:
            raise PermissionDenied("You cannot pay for another user's order")

        serializer.save()

        self._invalidate_payment_list_cache(order.user.id)

    def perform_update(self, serializer):
        if self.is_admin():
            raise PermissionDenied("You don't have permission to perform this action")
        serializer.save()

        self._invalidate_payment_list_cache(order.user.id)

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied("Orders cannot be deleted for archive purposes.")