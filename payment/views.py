import stripe
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from booking_status.models import BookingStatus
from order_status.models import OrderStatus
from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment_status.models import PaymentStatus
from user.permissions import IsUserOrAdmin
from flightsite.cache_keys import booking_list_cache_key as _booking_list_cache_key
from flightsite.cache_keys import payment_list_cache_key as _payment_list_cache_key

PAYMENT_LIST_CACHE_TIMEOUT = 300

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

    # validate that users can only create payments for their own orders, and admins cannot create payments at all
    def create(self, request, *args, **kwargs):
        if self.is_admin():
            raise PermissionDenied("Admins cannot create payments")
        order_id = request.data.get("order")
        if order_id:
            from order.models import Order
            try:
                order = Order.objects.get(pk=order_id)
                if order.user != request.user:
                    raise PermissionDenied("You cannot pay for another user's order")
            except Order.DoesNotExist:
                pass
        return super().create(request, *args, **kwargs)

    # Just creates the payment after validations
    def perform_create(self, serializer):
        order = serializer.validated_data.get("order")
        serializer.save()
        self._invalidate_payment_list_cache(order.user.id)

    def perform_update(self, serializer):
        raise PermissionDenied("Payment status cannot be updated directly.")

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied("Orders cannot be deleted for archive purposes.")

    @action(detail=False, methods=['get'], url_path='verify-session', permission_classes=[AllowAny])
    def verify_session(self, request):
        """Return payment status for a given Stripe payment intent ID."""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'detail': 'session_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        payment = (
            Payment.objects
            .select_related('payment_status', 'order__order_status')
            .filter(stripe_payment_session_id=session_id)
            .first()
        )
        if payment is None:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)


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

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session['payment_status'] == 'paid':
            _handle_payment_succeeded(session)
        else:
            _handle_payment_failed(session)
    elif event['type'] == 'checkout.session.expired':
        _handle_payment_failed(event['data']['object'])

    return HttpResponse(status=200)


def _handle_payment_succeeded(session):
    session_id = session['id']
    payment = (
        Payment.objects
        .select_related('order__order_status')
        .filter(stripe_payment_session_id=session_id)
        .first()
    )
    if payment is None:
        return

    completed_payment_status = PaymentStatus.objects.filter(code='COMPLETED').first()
    paid_order_status = OrderStatus.objects.filter(code='PAID').first()
    confirmed_booking_status = BookingStatus.objects.filter(code='CONFIRMED').first()

    if completed_payment_status:
        payment.payment_status = completed_payment_status
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


def _handle_payment_failed(session):
    session_id = session['id']
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