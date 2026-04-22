import stripe
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from booking.views import _booking_list_cache_key
from booking_status.models import BookingStatus
from order_status.models import OrderStatus
from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment_status.models import PaymentStatus
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
        raise PermissionDenied("Payment status cannot be updated directly.")

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied("Orders cannot be deleted for archive purposes.")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        _handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        _handle_payment_failed(event['data']['object'])

    return HttpResponse(status=200)


def _handle_payment_succeeded(payment_intent):
    session_id = payment_intent['id']
    payment = (
        Payment.objects
        .select_related('order__order_status')
        .filter(stripe_payment_session_id=session_id)
        .first()
    )
    if payment is None:
        return

    paid_payment_status = PaymentStatus.objects.filter(code='PAID').first()
    paid_order_status = OrderStatus.objects.filter(code='PAID').first()
    confirmed_booking_status = BookingStatus.objects.filter(code='CONFIRMED').first()

    if paid_payment_status:
        payment.payment_status = paid_payment_status
        payment.save()

    order = payment.order
    if paid_order_status and not order.order_status.is_terminal:
        order.order_status = paid_order_status
        order.save()

    if confirmed_booking_status:
        order.bookings.filter(booking_status__code='PENDING').update(
            booking_status=confirmed_booking_status
        )

    cache.delete(_payment_list_cache_key(order.user_id))
    cache.delete(_booking_list_cache_key(order.user_id))


def _handle_payment_failed(payment_intent):
    session_id = payment_intent['id']
    payment = (
        Payment.objects
        .select_related('order__order_status')
        .filter(stripe_payment_session_id=session_id)
        .first()
    )
    if payment is None:
        return

    failed_payment_status = PaymentStatus.objects.filter(code='FAILED').first()
    failed_order_status = OrderStatus.objects.filter(code='FAILED').first()

    if failed_payment_status:
        payment.payment_status = failed_payment_status
        payment.save()

    order = payment.order
    if failed_order_status and not order.order_status.is_terminal:
        order.order_status = failed_order_status
        order.save()

    cache.delete(_payment_list_cache_key(order.user_id))