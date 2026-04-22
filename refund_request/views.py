import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from booking.models import Booking
from django.core.cache import cache
from booking_status.models import BookingStatus
from order.models import Order
from order_status.models import OrderStatus
from payment_status.models import PaymentStatus
from refund_request.models import RefundRequest
from refund_request.serializers import RefundRequestSerializer
from user.permissions import IsAdmin, IsUserOrAdmin
from flightsite.cache_keys import booking_list_cache_key as _booking_list_cache_key
from flightsite.cache_keys import order_list_cache_key as _order_list_cache_key
from flightsite.cache_keys import payment_list_cache_key as _payment_list_cache_key


class RefundRequestViewSet(viewsets.ModelViewSet):
    queryset = RefundRequest.objects.select_related('order', 'booking')
    serializer_class = RefundRequestSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'approve', 'reject'):
            return [IsAdmin()]
        return [IsUserOrAdmin()]

    def is_admin(self):
        return self.request.user.role == 'admin'

    def get_queryset(self):
        if self.is_admin():
            qs = RefundRequest.objects.select_related('order', 'booking')
            if status_filter := self.request.query_params.get('status'):
                qs = qs.filter(status=status_filter.upper())
            return qs
        return RefundRequest.objects.none()

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        booking = serializer.validated_data.get('booking')

        if self.is_admin():
            raise PermissionDenied("Admins cannot create refund requests.")

        if order.user_id != self.request.user.id:
            raise PermissionDenied("Not your order.")

        if booking and booking.order_id != order.id:
            raise PermissionDenied("Booking does not belong to this order.")

        if RefundRequest.objects.filter(order=order, booking=booking, status='PENDING').exists():
            raise PermissionDenied("A pending refund request already exists.")

        serializer.save()

    def perform_update(self, serializer):
        raise PermissionDenied("Use approve or reject actions.")

    def perform_destroy(self, instance):
        raise PermissionDenied("Refund requests cannot be deleted.")

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        refund_request = get_object_or_404(RefundRequest.objects.select_related('order', 'booking'), pk=pk)

        if not self.is_admin():
            raise PermissionDenied("Only admins can approve refund requests.")

        if refund_request.status != 'PENDING':
            return Response({'detail': 'Only pending refund requests can be approved.'}, status=status.HTTP_400_BAD_REQUEST)

        order = refund_request.order
        payment = order.payments.select_related('payment_status').filter(payment_status__code='PAID').first()
        if payment is None:
            return Response({'detail': 'No paid payment found for this order.'}, status=status.HTTP_400_BAD_REQUEST)

        if refund_request.is_order_refund:
            refund_amount = None
        else:
            refund_amount = int(refund_request.booking.fare_price * 100)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_kwargs = {'payment_intent': payment.stripe_payment_session_id}
            if refund_amount is not None:
                stripe_kwargs['amount'] = refund_amount
            stripe.Refund.create(**stripe_kwargs)
        except stripe.error.StripeError as e:
            return Response({'detail': f'Stripe refund failed: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)

        refund_request.status = 'APPROVED'
        refund_request.processed_at = timezone.now()
        refund_request.save()

        refunded_payment_status = PaymentStatus.objects.filter(code='REFUNDED').first()
        if refunded_payment_status:
            payment.payment_status = refunded_payment_status
            payment.save()

        if refund_request.is_order_refund:
            _apply_order_refund(order)
        else:
            _apply_booking_refund(refund_request.booking, order)

        cache.delete(_booking_list_cache_key(order.user_id))
        cache.delete(_order_list_cache_key(order.user_id))
        cache.delete(_payment_list_cache_key(order.user_id))

        return Response(RefundRequestSerializer(refund_request).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        refund_request = get_object_or_404(RefundRequest, pk=pk)

        if not self.is_admin():
            raise PermissionDenied("Only admins can reject refund requests.")

        if refund_request.status != 'PENDING':
            return Response({'detail': 'Only pending refund requests can be rejected.'}, status=status.HTTP_400_BAD_REQUEST)

        refund_request.status = 'REJECTED'
        refund_request.processed_at = timezone.now()
        refund_request.save()

        return Response(RefundRequestSerializer(refund_request).data)


def _apply_order_refund(order):
    refunded_booking_status = BookingStatus.objects.filter(code='REFUNDED').first()
    if refunded_booking_status:
        order.bookings.all().update(booking_status=refunded_booking_status)

    refunded_order_status = OrderStatus.objects.filter(code='REFUNDED').first()
    if refunded_order_status:
        order.order_status = refunded_order_status
        order.save()


def _apply_booking_refund(booking, order):
    refunded_booking_status = BookingStatus.objects.filter(code='REFUNDED').first()
    if refunded_booking_status:
        booking.booking_status = refunded_booking_status
        booking.save()

    total = order.bookings.count()
    # count after saving the booking above so the current booking is included
    refunded_count = order.bookings.filter(booking_status__code='REFUNDED').count()

    if refunded_count == total:
        new_code = 'REFUNDED'
    elif refunded_count:
        new_code = 'PARTIALLY_REFUNDED'
    else:
        return

    new_order_status = OrderStatus.objects.filter(code=new_code).first()
    if new_order_status:
        order.order_status = new_order_status
        order.save()
